import os
import json
import config
from datetime import datetime
import gsheets
import serpapi
import airportsdata
from email_alert import sendEmail
from db_transactions import insert_new_flight_observation
from token_refresh import main as token_refresh_main

AIRPORTS = airportsdata.load("IATA") 

RUNTIME_DIR = config.RUNTIME_DIR
PATHS = config.PATHS

def ensure_runtime_files_exist():
    os.makedirs(RUNTIME_DIR, exist_ok=True)

    for path in PATHS.values():
        with open(path, "a"):
            pass


# API querystring that imports the parameters set in the config.py file
# Comment out any parameters that you left blank in config.py, or if you want to omit them from the search query
QUERYSTRING = {
    "engine":config.ENGINE,
    "hl":config.HL,
    "gl":config.GL,
    "type":config.TYPE,
    "departure_id":config.DEPARTURE_ID,
    "arrival_id":config.ARRIVAL_ID,
    "outbound_date":config.OUTBOUND_DATE,
    "return_date":config.RETURN_DATE,
    "travel_class":config.TRAVEL_CLASS,
    "adults":config.ADULTS,
    "children":config.CHILDREN,
    "stops":config.STOPS,
    "currency":config.CURRENCY,
    "show_hidden":config.SHOW_HIDDEN,
    "sort_by":config.SORT_BY,
}


# Actual API call, uses google flights form serpAPI
def callAPI():
    try:
        client = serpapi.Client(api_key=config.SERPAPI_KEY)
        response = client.search(**QUERYSTRING)

        if "error" in response:
            print(f"SerpAPI error: {response['error']}")
            return "Error", []
        
        status = response.get("search_metadata", {}).get("status")

        if status != "Success":
            print(f"SerpAPI search failed. Status: {status}")
            print(json.dumps(response, indent=4))
            return status or "Error", []

        best_flights = response.get("best_flights", [])
        other_flights = response.get("other_flights", [])

        results = best_flights + other_flights

        if not results:
            print("SerpApi request succeeded, but no flights were returned.")
            return status, []

        with open(PATHS["search_flights_response"], "w+", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)


        return status, results
    
    except KeyError as e:
        print(f"Missing expected field in SerpApi response: {e}")
        return "Error", []

    except Exception as e:
        print(f"SerpApi request failed: {type(e).__name__}: {e}")
        return "Error", []


def get_airport_city(iata_code):
    airport = AIRPORTS.get(iata_code)
    if airport:
        return airport.get("city", "")
    else:
        return ""


# Convert the flight departure/arrival time from timestamp to generic time of day for better interpretation in data set
def getTimeOfDay(flightTime: str) -> str:
    dt = datetime.fromisoformat(flightTime)
    hour = dt.hour

    if 4 <= hour < 8:
        return "early morning"
    elif 8 <= hour < 12:
        return "morning"
    elif 12 <= hour < 16:
        return "afternoon"
    elif 16 <= hour < 20:
        return "evening"
    elif 20 <= hour < 24:
        return "night"
    else:
        return "late night"


# Convert the flight duration response from minutes to hours
def getFlightDuration(duration: str) -> str:
    duration_float = float(duration)
    flight_hours = round((duration_float / 60), 2)

    return str(flight_hours)


# Write specifed data to 'flight_alert.txt'
def flightAlert(data: dict):
    with open(PATHS["flight_alert"], "a") as file:
        file.write(f"{data["source_airport"]} --> {data["destination_airport"]}, {data["departure_date"]} --> {data["return_date"]}\n"
                   f"{data["airline"]}, Flight Number: {data["flight_code"]}, {data["stops"]} Stops, {data["duration"]} Hours\n"
                   f"{data["class"]}, {data["itinerary_type"]}, {data["total_cost"]} {data["currency"]}\n\n")
                   

# Search through the response data for flight info and prices
def searchFlightOffers(data):
    day_of_week = datetime.now().strftime('%A')
    
    with open(os.path.join(PATHS["flight_data"]), "w+") as file:
        for flight_offer in data:
            flights = flight_offer.get("flights", [])

            if not flights:
                continue
            
            first_leg = flights[0]
            last_leg = flights[-1]

            source_airport = first_leg["departure_airport"]
            destination_airport = last_leg["arrival_airport"]

            source_city = get_airport_city(source_airport.get("id"))
            destination_city = get_airport_city(destination_airport.get("id"))

            total_cost = flight_offer.get("price")
            currency = config.CURRENCY

            airline = first_leg.get("airline")
            flight_code = "_".join(
                leg.get("flight_number", "").replace(" ", "")
                for leg in flights
            )
            travel_class = first_leg.get("travel_class")
            itinerary_type = flight_offer.get("type")

            stops = len(flights) - 1
            duration = getFlightDuration(flight_offer.get("total_duration"))

            departure_time = getTimeOfDay(source_airport.get("time"))
            arrival_time = getTimeOfDay(destination_airport.get("time"))

            # Writes to file in CSV format, can comment out if you don't need it
            file.write(
                f"{airline},{flight_code},{source_city},{source_airport.get('id')},"
                f"{departure_time},{stops},{duration},{destination_city},"
                f"{destination_airport.get('id')},{arrival_time},{travel_class},{itinerary_type},"
                f"{currency},{total_cost},{day_of_week},"
                f"{datetime.today().strftime('%Y/%m/%d')},{config.OUTBOUND_DATE},{config.RETURN_DATE}\n")
            
            # # Saves specified data in a dictionary to then be formatted in the email body if it meets the PRICE_THRESHOLD
            if total_cost is not None and total_cost <= config.PRICE_THRESHOLD:
                alert_data = {
                    "airline":airline,
                    "flight_code":flight_code,
                    "source_airport":source_airport.get("id"),
                    "stops":stops,
                    "duration":duration,
                    "destination_airport":destination_airport.get("id"),
                    "class":travel_class,
                    "itinerary_type":itinerary_type,
                    "total_cost":total_cost,
                    "currency":currency,
                    "departure_date":config.OUTBOUND_DATE,
                    "return_date":config.RETURN_DATE
                }
                flightAlert(alert_data)


def main():
    try:
        ensure_runtime_files_exist()
    except Exception as e:
        print(f"Failed to create necessary runtime directory/files. {e}")
        return

    response, data = callAPI()

    if response != "Success":
        print(f"SearchFlight response returned False with status: {response}")
        return

    if not data:
        print("SearchFlight response succeeded, but no flight data was returned.")
        return

    try:
        searchFlightOffers(data)
    except Exception as e:
        print(f"Failed to process flight data. {e}")
        return

    feature_functions = [
        sendEmail,
        insert_new_flight_observation,
        gsheets.main
    ]

    for func in feature_functions:
        try:
            func()
        except Exception as e:
            print(f"The function {func.__name__} failed to complete. {e}")
            if func is gsheets.main and isinstance(
                e, gsheets.GoogleSheetsAuthenticationError
            ):
                print("Google authentication failed; requesting a new token.")
                try:
                    token_refresh_main()
                except Exception as refresh_error:
                    print(
                        "Google Sheets authentication retry failed. "
                        f"{type(refresh_error).__name__}: {refresh_error}"
                    )



if __name__ == "__main__":
    main()
