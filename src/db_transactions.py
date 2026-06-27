import psycopg2, os, csv
from config import DB_PASSWORD, PATHS


def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="flight-data",
        user="postgres",
        password=DB_PASSWORD,
        port=5432
    )


def insert_new_flight_observation():
    conn = None
    cur = None

    insert_query = """
        INSERT INTO staging_flight_observations (
            source_system,
            source_file,
            source_row_number,
            airline,
            flight_code,
            source_city,
            source_airport,
            departure_time,
            stops,
            duration,
            destination_city,
            destination_airport,
            arrival_time,
            class,
            itinerary_type,
            currency,
            total_cost,
            day_searched,
            timestamp_searched,
            departure_date,
            return_date
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        );
    """

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        source_file = os.path.basename(PATHS["flight_data"])

        with open(PATHS["flight_data"], "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            
            for source_row_number, row in enumerate(reader, start=1):
                values = (
                    "serpapi_google_flights",
                    source_file,
                    source_row_number,
                    *row,
                )
                cur.execute(insert_query, values)
                
        conn.commit()
        print("New flight observations inserted successfully.")       

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Failed to insert new observations: {e}")
        
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def main():
    insert_new_flight_observation()


if __name__ == "__main__":
    main()