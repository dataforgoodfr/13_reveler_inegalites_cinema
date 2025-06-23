def parse_age(value):
    """
    Safely parses a value into a minimum age integer.

    - Converts strings like '70+' to 70.
    - Returns None for:
        - NaN/missing values
        - Zero (0)
        - Invalid or non-numeric input (e.g., 'abc')
    - Returns the integer value otherwise.

    Args:
        value: The input value to parse (can be a string, int, float, or NaN).

    Returns:
        int or None: A valid minimum age integer or None if input is invalid or zero.
    """
    try:
        if isinstance(value, str) and value.endswith('+'):
            value = value.rstrip('+')
        return_val = int(value)
        return return_val if return_val != 0 else None
    except (ValueError, TypeError):
        return None