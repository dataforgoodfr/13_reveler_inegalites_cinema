import pytest
from datetime import date
from backend.utils.date_utils import parse_release_date, parse_duration

class TestParseReleaseDate:
    @pytest.mark.parametrize("input_str, expected", [
        ("12 janvier 2023", date(2023, 1, 12)),
        ("01 février 2020", date(2020, 2, 1)),
        ("31 décembre 1999", date(1999, 12, 31)),
        ("29 octobre 2025", date(2025, 10, 29)),
        ("", None),
        ("not a date", None),
    ])
    def test_valid_and_invalid_dates(self, input_str, expected):
        assert parse_release_date(input_str) == expected

class TestParseDuration:
    @pytest.mark.parametrize("input_str, expected", [
        ("2h00min", 120),
        ("1h45min", 105),
        ("0h10min", 10),
        ("1h", 60),
        ("90min", 90),
        ("3h40min", 220),
        ("", None),
        ("weird input", None),
    ])
    def test_various_duration_formats(self, input_str, expected):
        assert parse_duration(input_str) == expected
