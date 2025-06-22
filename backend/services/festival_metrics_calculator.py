from typing import List, Dict, Optional


def calculate_female_director_representation(nominated_directors: List[Dict]) -> Dict[str, Optional[float]]:
    """
    Calculates the percentage of female nominated directors among all known-gender nominated directors
    for nominated and awarded films at a festival in a given year.

    A film is considered "nominated" if it appears in the list.
    A film is considered "awarded" if it has at least one director credit with `film_is_winner=True`.

    Unknown genders are excluded.

    Args:
        nominated_directors (List[Dict]): List of dicts with:
            - film_id (int)
            - director_gender (str or None)
            - film_is_winner (bool)

    Returns:
        Dict[str, Optional[float]]: {
            "nominated": percentage of female nominated directors (0 100) or None,
            "awarded": percentage of female awarded directors (0 100) or None,
        }
    """

    nominated_female = 0
    nominated_total = 0

    awarded_female = 0
    awarded_total = 0

    for d in nominated_directors:
        gender = (d["director_gender"] or "").lower()
        if gender not in {"female", "male"}:
            continue

        nominated_total += 1
        if gender == "female":
            nominated_female += 1

        if d["film_is_winner"]:
            awarded_total += 1
            if gender == "female":
                awarded_female += 1

    return {
        "nominated": round((nominated_female / nominated_total) * 100) if nominated_total else None,
        "awarded": round((awarded_female / awarded_total) * 100) if awarded_total else None,
    }
