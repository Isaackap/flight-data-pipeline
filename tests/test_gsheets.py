import gsheets


def test_read_text_returns_comma_split_rows(tmp_path, monkeypatch):
    flight_data = tmp_path / "flight_data.txt"
    flight_data.write_text(
        "United,UA123,Houston,Tokyo\nDelta,DL42,Atlanta,Paris\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(gsheets, "PATHS", {"flight_data": str(flight_data)})

    assert gsheets.readText() == [
        ["United", "UA123", "Houston", "Tokyo\n"],
        ["Delta", "DL42", "Atlanta", "Paris\n"],
    ]
