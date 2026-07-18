SELECT
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
    return_date,
    COUNT(*) AS duplicate_count
FROM staging_flight_observations
GROUP BY
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
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

-- Result summary as of 2026-07-01:
-- duplicate_groups: 765
-- rows_in_duplicate_groups: 2154
-- extra_duplicate_rows: 1389
-- largest_group: 24