SELECT
    airline,
    source_city,
    destination_city,
    departure_date,
    COUNT(*) AS airline_count,
    ROUND(AVG(total_cost), 2) AS average_cost
FROM staging_flight_observations
WHERE destination_city = 'Tokyo'
    AND TO_CHAR(departure_date, 'MM-DD') = '01-06'
GROUP BY
    airline,
    source_city,
    destination_city,
    departure_date
ORDER BY average_cost DESC;


-- "airline",            "source_city","destination_city","departure_date","airline_count","average_cost"
-- "British Airways",    "Houston",    "Tokyo",           "2027-01-06",    "25",           "3736.20"
-- "Aeromexico",         "Houston",    "Tokyo",           "2027-01-06",    "27",           "3565.70"
-- "Emirates",           "Houston",    "Tokyo",           "2027-01-06",    "38",           "2961.34"
-- "Delta",              "Houston",    "Tokyo",           "2027-01-06",    "150",          "2466.07"
-- "American",           "Houston",    "Tokyo",           "2027-01-06",    "464",          "2449.36"
-- "JetBlue",            "Houston",    "Tokyo",           "2027-01-06",    "10",           "2277.90"
-- "United",             "Houston",    "Tokyo",           "2027-01-06",    "1675",         "2115.02"
-- "ANA",                "Houston",    "Tokyo",           "2027-01-06",    "22",           "2088.18"
-- "Air France",         "Houston",    "Tokyo",           "2027-01-06",    "8",            "2078.75"
-- "All Nippon Airways", "Houston",    "Tokyo",           "2027-01-06",    "246",          "2010.64"
-- "WestJet",            "Houston",    "Tokyo",           "2027-01-06",    "41",           "2006.49"
-- "United Airlines",    "Houston",    "Tokyo",           "2027-01-06",    "215",          "1990.17"
-- "Alaska",             "Houston",    "Tokyo",           "2027-01-06",    "77",           "1914.61"
-- "Air Canada",         "Houston",    "Tokyo",           "2027-01-06",    "58",           "1911.10"
-- "Qatar Airways",      "Houston",    "Tokyo",           "2027-01-06",    "30",           "1869.80"
-- "EVA Air",            "Houston",    "Tokyo",           "2027-01-06",    "123",          "1783.29"
-- "Japan Airlines",     "Houston",    "Tokyo",           "2027-01-06",    "18",           "1707.56"
-- "American Airlines",  "Houston",    "Tokyo",           "2027-01-06",    "8",            "1579.50"
-- "Lufthansa",          "Houston",    "Tokyo",           "2027-01-06",    "42",           "1529.26"
-- "Turkish Airlines",   "Houston",    "Tokyo",           "2027-01-06",    "66",           "1374.88"
-- "All Nippon Airways", "Houston",    "Tokyo",           "2026-01-06",    "295",          "1138.65"
-- "United Airlines",    "Houston",    "Tokyo",           "2026-01-06",    "832",          "1093.81"
-- "American Airlines",  "Houston",    "Tokyo",           "2026-01-06",    "54",           "1082.13"
-- "Japan Airlines",     "Houston",    "Tokyo",           "2026-01-06",    "12",           "1034.17"
