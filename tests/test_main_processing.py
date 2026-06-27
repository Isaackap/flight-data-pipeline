from datetime import datetime as real_datetime

import main


class FixedDatetime:
    @classmethod
    def now(cls):
        return real_datetime(2026, 6, 26, 10, 30)

    @classmethod
    def today(cls):
        return real_datetime(2026, 6, 26, 10, 30)

    @classmethod
    def fromisoformat(cls, value):
        return real_datetime.fromisoformat(value)


def test_ensure_runtime_files_exist_creates_directory_and_files(tmp_path, monkeypatch):
    runtime_dir = tmp_path / "runtime"
    paths = {
        "flight_data": str(runtime_dir / "flight_data.txt"),
        "flight_alert": str(runtime_dir / "flight_alert.txt"),
        "search_flights_response": str(runtime_dir / "search_flights_response.json"),
    }

    monkeypatch.setattr(main, "RUNTIME_DIR", str(runtime_dir))
    monkeypatch.setattr(main, "PATHS", paths)

    main.ensure_runtime_files_exist()

    assert runtime_dir.is_dir()
    assert all((tmp_path / "runtime" / filename).is_file() for filename in [
        "flight_data.txt",
        "flight_alert.txt",
        "search_flights_response.json",
    ])


def test_get_time_of_day_boundaries():
    assert main.getTimeOfDay("2027-01-06T03:59:00") == "late night"
    assert main.getTimeOfDay("2027-01-06T04:00:00") == "early morning"
    assert main.getTimeOfDay("2027-01-06T08:00:00") == "morning"
    assert main.getTimeOfDay("2027-01-06T12:00:00") == "afternoon"
    assert main.getTimeOfDay("2027-01-06T16:00:00") == "evening"
    assert main.getTimeOfDay("2027-01-06T20:00:00") == "night"
    assert main.getTimeOfDay("2027-01-06T00:00:00") == "late night"


def test_get_flight_duration_converts_minutes_to_hours():
    assert main.getFlightDuration("90") == "1.5"
    assert main.getFlightDuration("95") == "1.58"


def test_get_airport_city_returns_city_or_empty_string(monkeypatch):
    monkeypatch.setattr(main, "AIRPORTS", {"IAH": {"city": "Houston"}})

    assert main.get_airport_city("IAH") == "Houston"
    assert main.get_airport_city("XXX") == ""


def test_flight_alert_appends_human_readable_alert(tmp_path, monkeypatch):
    alert_file = tmp_path / "flight_alert.txt"
    monkeypatch.setattr(main, "PATHS", {"flight_alert": str(alert_file)})

    main.flightAlert({
        "source_airport": "IAH",
        "destination_airport": "HND",
        "departure_date": "2027-01-06",
        "return_date": "2027-01-20",
        "airline": "United",
        "flight_code": "UA123",
        "stops": 0,
        "duration": "13.5",
        "class": "Economy",
        "itinerary_type": "Round trip",
        "total_cost": 999,
        "currency": "USD",
    })

    assert alert_file.read_text(encoding="utf-8") == (
        "IAH --> HND, 2027-01-06 --> 2027-01-20\n"
        "United, Flight Number: UA123, 0 Stops, 13.5 Hours\n"
        "Economy, Round trip, 999 USD\n\n"
    )


def test_search_flight_offers_writes_csv_and_alert_for_prices_below_threshold(
    tmp_path,
    monkeypatch,
):
    flight_data = tmp_path / "flight_data.txt"
    flight_alert = tmp_path / "flight_alert.txt"
    monkeypatch.setattr(main, "PATHS", {
        "flight_data": str(flight_data),
        "flight_alert": str(flight_alert),
    })
    monkeypatch.setattr(main, "datetime", FixedDatetime)
    monkeypatch.setattr(main.config, "CURRENCY", "USD")
    monkeypatch.setattr(main.config, "PRICE_THRESHOLD", 1000)
    monkeypatch.setattr(main.config, "OUTBOUND_DATE", "2027-01-06")
    monkeypatch.setattr(main.config, "RETURN_DATE", "2027-01-20")
    monkeypatch.setattr(
        main,
        "get_airport_city",
        lambda iata_code: {"IAH": "Houston", "HND": "Tokyo"}[iata_code],
    )

    offers = [
        {
            "flights": [
                {
                    "departure_airport": {"id": "IAH", "time": "2027-01-06T07:30:00"},
                    "arrival_airport": {"id": "LAX", "time": "2027-01-06T09:15:00"},
                    "airline": "United",
                    "flight_number": "UA 123",
                    "travel_class": "Economy",
                },
                {
                    "departure_airport": {"id": "LAX", "time": "2027-01-06T11:00:00"},
                    "arrival_airport": {"id": "HND", "time": "2027-01-07T20:45:00"},
                    "airline": "United",
                    "flight_number": "UA 456",
                    "travel_class": "Economy",
                },
            ],
            "price": 999,
            "type": "Round trip",
            "total_duration": "450",
        },
        {"flights": []},
    ]

    main.searchFlightOffers(offers)

    assert flight_data.read_text(encoding="utf-8") == (
        "United,UA123_UA456,Houston,IAH,early morning,1,7.5,Tokyo,HND,"
        "night,Economy,Round trip,USD,999,Friday,2026/06/26,2027-01-06,2027-01-20\n"
    )
    assert flight_alert.read_text(encoding="utf-8") == (
        "IAH --> HND, 2027-01-06 --> 2027-01-20\n"
        "United, Flight Number: UA123_UA456, 1 Stops, 7.5 Hours\n"
        "Economy, Round trip, 999 USD\n\n"
    )
