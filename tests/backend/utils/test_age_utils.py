import pytest
from backend.utils.age_utils import parse_age

class TestParseAgeMin:
    @pytest.mark.parametrize("input_value, expected", [
        (25, 25),
        ("30", 30),
        ("70+", 70),
        ("90+", 90),
        (0, None),
        ("0", None),
        ("", None),
        (None, None),
        ("abc", None),
        (float("nan"), None),
    ])
    def test_parse_age(self, input_value, expected):
        assert parse_age(input_value) == expected
