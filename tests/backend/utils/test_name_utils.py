from backend.utils.name_utils import split_full_name, guess_gender, remove_extra_spaces
import pytest

class TestSplitFullName:
    def test_basic(self):
        assert split_full_name("John Doe") == ("John", "Doe")

    def test_single(self):
        assert split_full_name("Madonna") == ("Madonna", "")

    def test_empty(self):
        assert split_full_name("") == ("", "")

    def test_with_middle(self):
        assert split_full_name("John Michael Doe") == ("John", "Doe")
    
    def test_with_hyphen(self):
        assert split_full_name("Jean-Paul Belmondo") == ("Jean-Paul", "Belmondo")

    def test_with_middle_with_point(self):
        assert split_full_name("John M. Doe") == ("John", "Doe")

class TestGuessGender:
    def test_male(self):
        assert guess_gender("John") == "male"
        assert guess_gender("Hervé") == "male"

    def test_female(self):
        assert guess_gender("Emily") == "female"
        assert guess_gender("Frédérique") == "female"

    def test_mostly(self):
        assert guess_gender("Taylor") == "male"
        assert guess_gender("Camille") == "female"
    
    def test_andy(self):
        assert guess_gender("Pauley") == "unknown"

    def test_unknown(self):
        assert guess_gender("Kio") == "unknown"

class TestRemoveExtraSpaces:
    @pytest.mark.parametrize("input_str, expected", [
        ("John  Doe", "John Doe"),
        ("   Jean   Dupont   ", "Jean Dupont"),
        ("A   B   C", "A B C"),
        ("NoExtraSpaces", "NoExtraSpaces"),
        ("", ""),
        ("   ", "")
    ])
    def test_space_cleanup(self, input_str, expected):
        assert remove_extra_spaces(input_str) == expected