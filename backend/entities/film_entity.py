BUDGET_CATEGORIES = [
    {"name": "Moins de 2 M€",    "min": 0,              "max": 2_000_000},
    {"name": "2 à 5 M€",         "min": 2_000_000,      "max": 5_000_000},
    {"name": "5 à 10 M€",        "min": 5_000_000,      "max": 10_000_000},
    {"name": "10 à 20 M€",       "min": 10_000_000,     "max": 20_000_000},
    {"name": "Plus de 20 M€",    "min": 20_000_000,     "max": float('inf')},
]

class FilmEntity:
    @staticmethod
    def budget_category(budget_str: str) -> str | None:
        """
        Return the budget category name for a given budget string in millions (e.g. '4.5').

        Args:
            budget_str (str): Budget in millions as a string with dot decimal (e.g., '3.2').

        Returns:
            str | None: The name of the budget category, or None if invalid input.
        """
        try:
            budget = float(budget_str)
        except (ValueError, TypeError):
            return None

        for category in BUDGET_CATEGORIES:
            if category["min"] <= budget < category["max"]:
                return category["name"]
        return None