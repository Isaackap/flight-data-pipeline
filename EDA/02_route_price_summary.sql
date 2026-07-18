SELECT
    source_city,
    source_airport,
    destination_city,
    destination_airport,
    ROUND(MIN(total_cost), 2) AS minimum_cost,
    ROUND(AVG(total_cost), 2) AS average_cost,
    ROUND(MAX(total_cost), 2) AS maximum_cost,
    COUNT(*) AS flight_count
FROM staging_flight_observations
WHERE destination_city = 'Tokyo'
    AND TO_CHAR(departure_date, 'MM-DD') = '01-06'
GROUP BY
    source_city,
    source_airport,
    destination_city,
    destination_airport
ORDER BY average_cost;

-- "source_city","source_airport","destination_city","destination_airport","minimum_cost","average_cost","maximum_cost","flight_count"
-- "Houston"    ,"IAH"           ,"Tokyo"           ,"HND"                ,"1004.00"     ,"1700.30"     ,"8683.00"     ,"3123"
-- "Houston"    ,"IAH"           ,"Tokyo"           ,"NRT"                ,"1202.00"     ,"2250.69"     ,"9257.00"     ,"1413"

