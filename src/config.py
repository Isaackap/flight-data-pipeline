import os
from dotenv import load_dotenv
from google.cloud import secretmanager

load_dotenv()


# ------------------------------------------------------------- Google Cloud Configurations Below ------------------------------------------------------------

# Pulls private variables from Google Cloud hosted in their Secrets Manager
def access_secret(project_id: str, secret_id: str, version: str = "latest") -> str:
    name = (
        f"projects/{project_id}/secrets/"
        f"{secret_id}/versions/{version}"
    )

    try:
        response = secret_client.access_secret_version(
            request={"name": name}
        )
    except Exception as exc:
        raise RuntimeError(
            f"Unable to load required secret: {secret_id}"
        ) from exc

    secret_value = response.payload.data.decode("UTF-8").rstrip("\r\n")

    if not secret_value:
        raise RuntimeError(
            f"Secret {secret_id} is empty. Please check the secret value."
        )

    return secret_value


secret_client = secretmanager.SecretManagerServiceClient()

GOOGLE_CLOUD_PROJECT_ID = "flightdata-465603"
DB_PASSWORD = access_secret(GOOGLE_CLOUD_PROJECT_ID, "Database_Password")
FROM_EMAIL = access_secret(GOOGLE_CLOUD_PROJECT_ID, "SenderEmail")
TO_EMAIL = access_secret(GOOGLE_CLOUD_PROJECT_ID, "ReceiverEmail")
EMAIL_PASSWORD = access_secret(GOOGLE_CLOUD_PROJECT_ID, "GoogleApp_Password")
SERPAPI_KEY = access_secret(GOOGLE_CLOUD_PROJECT_ID, "SERPAPI_KEY")
SPREADSHEET_ID = access_secret(GOOGLE_CLOUD_PROJECT_ID, "Spreadsheet_ID")


# ------------------------------------------------------------- General Configurations Below ------------------------------------------------------------

RUNTIME_DIR = "runtime-outputs"
PATHS = {
    "flight_data": os.path.join(RUNTIME_DIR, "flight_data.txt"),
    "flight_alert": os.path.join(RUNTIME_DIR, "flight_alert.txt"),
    "search_flights_response": os.path.join(RUNTIME_DIR, "search_flights_response.json")
}

# DB_PASSWORD = os.getenv("DB_PASSWORD")


# ------------------------------------------------------------- Email Configurations Below ------------------------------------------------------------

# Parameters for sending the email/alert of flight offers.
# The Sender and Receiver email info will be imported from the local .env file as well as the Sender email password (Use app password if 2FA is enabled)
# FROM_EMAIL = os.getenv("SENDER_EMAIL")
# TO_EMAIL = os.getenv("RECEIVER_EMAIL")
# EMAIL_PASSWORD = os.getenv("PASSWORD")
# Parameters for the email server, only variable that needs changing is the 'SMTP_SERVER', adjust it to your sender email
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
# The subject text of the email, set it to whatever you desire
EMAIL_SUBJECT = "FlightScript Price Alert"


# ------------------------------------------------------------- API Configurations below --------------------------------------------------------------

# SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# This query takes 11 total parameters, some are optional
# Replace the following variables with the data you desire for your flight search, following the correct format

# Set the desired price point to recieve alerts on flight prices
# Make sure the currency matches the set "CURRENCY_CODE" parameter down below
PRICE_THRESHOLD = 1100

# The search engine to use for the flight search, currently only supports Google Flights
ENGINE = "google_flights"

# The language and country code (2 letters) for the google flights search engine.
HL = "en"
GL = "us"

# Parameter defines the type of the flights.
# 1 - Round trip (default)
# 2 - One way
# 3 - Multi-city
TYPE = "1"

# The airport code (usually 3 letters)
# Example is the George Bush Intercontinental Airport in Houston, TX. Airport code is 'IAH'"
# You can specify multiple departure airports by separating them with a comma. For example, CDG,ORY
# From/Departure location Id
DEPARTURE_ID = "IAH"

# To/Arrival location Id, follows same rules as the FROM_ID
ARRIVAL_ID = "HND,NRT"

# Departure or travel date. Format: YYYY-MM-DD
OUTBOUND_DATE = "2027-01-06"

# Return date. Format: YYYY-MM-DD
RETURN_DATE = "2027-01-20"

# Specifies the preferred cabin class, such as Economy, Premium Economy, Business, or First Class.
# Available Travel Class: 1 - ECONOMY (default), 2 - PREMIUM_ECONOMY, 3 - BUSINESS, or 4 - FIRST
TRAVEL_CLASS = 1

# The number of guests who are 18 years in age or older. The default value is set to 1
ADULTS = 1

# The number of children under 18 years of age. Default is 0
CHILDREN = 0

# Filters flights based on the number of stops. Accepted values are:
# 0 for any number of stops (default)
# 1 for non-stop flights
# 2 for one-stop flights
# 3 for two-stop flights
STOPS = 0

# Sets the currency for price formatting in the response. Default is USD
CURRENCY = "USD"

# Set to true to include the hidden flight results. This is equivalent to clicking 'View more flights' on Google Flights.
# Default to false
SHOW_HIDDEN = True

# Sort by parameter
# 1 - Top flights (default)
# 2 - Price
# 3 - Departure time
# 4 - Arrival time
# 5 - Duration
# 6 - Emissions
SORT_BY = "1"

