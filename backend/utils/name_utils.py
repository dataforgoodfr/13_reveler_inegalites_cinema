import gender_guesser.detector as gender
import re

_gender_detector = gender.Detector()

def split_full_name(full_name: str) -> tuple:
    parts = full_name.strip().split()
    if len(parts) == 0:
        return ("", "")
    elif len(parts) == 1:
        return (parts[0], "")
    else:
        return (parts[0], parts[-1])

def guess_gender(first_name: str) -> str:
    gender = _gender_detector.get_gender(first_name)
    if gender in ['male', 'mostly_male']:
        return 'male'
    elif gender in ['female', 'mostly_female']:
        return 'female'
    else:
        return 'unknown'

def remove_extra_spaces(s: str) -> str:
    if not isinstance(s, str):
        raise ValueError("Input must be a string", s)
    return re.sub(r'\s+', ' ', s).strip()
