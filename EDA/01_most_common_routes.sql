SELECT
    source_city,
    source_airport,
    destination_city,
    destination_airport,
    COUNT(*) AS flight_count
FROM staging_flight_observations
WHERE destination_city = 'Tokyo'
    AND TO_CHAR(departure_date, 'MM-DD') = '01-06'
GROUP BY source_city, source_airport, destination_city, destination_airport
ORDER BY flight_count DESC;

-- "source_city","source_airport","destination_city","destination_airport","flight_count"
-- "Houston"    ,"IAH"           ,"Tokyo"           ,"HND"                ,"3123"
-- "Houston"    ,"IAH"           ,"Tokyo"           ,"NRT"                ,"1413"
