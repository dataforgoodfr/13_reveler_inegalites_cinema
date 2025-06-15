BUDGET_CATEGORIES = [
    {"name": "Moins de 2 M€",    "min": 0,              "max": 2_000_000},
    {"name": "2 à 5 M€",         "min": 2_000_000,      "max": 5_000_000},
    {"name": "5 à 10 M€",        "min": 5_000_000,      "max": 10_000_000},
    {"name": "10 à 20 M€",       "min": 10_000_000,     "max": 20_000_000},
    {"name": "Plus de 20 M€",    "min": 20_000_000,     "max": float('inf')},
]

GENRE_CATEGORIES = {
    "animation": "Animation",
    "action": "Aventure/Policier/Thriller",
    "arts martiaux": "Aventure/Policier/Thriller",
    "aventure": "Aventure/Policier/Thriller",
    "espionnage": "Aventure/Policier/Thriller",
    "judiciaire": "Aventure/Policier/Thriller",
    "policier": "Aventure/Policier/Thriller",
    "thriller": "Aventure/Policier/Thriller",
    "western": "Aventure/Policier/Thriller",
    "biopic": "Biopic/Guerre/Histoire",
    "guerre": "Biopic/Guerre/Histoire",
    "historique": "Biopic/Guerre/Histoire",
    "péplum": "Biopic/Guerre/Histoire",
    "comédie": "Comédie/Comédie dramatique",
    "comédie dramatique": "Comédie/Comédie dramatique",
    "comédie musicale": "Comédie/Comédie dramatique",
    "famille": "Comédie/Comédie dramatique",
    "musical": "Comédie/Comédie dramatique",
    "romance": "Comédie/Comédie dramatique",
    "documentaire": "Documentaire",
    "drame": "Drame",
    "opéra": "Drame",
    "épouvante-horreur": "Fantastique/Horreur/SF",
    "expérimental": "Fantastique/Horreur/SF",
    "fantastique": "Fantastique/Horreur/SF",
    "science fiction": "Fantastique/Horreur/SF",
    # Excluded entries like "divers", "erotique" and "événement sportif"
}

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
    
    @staticmethod
    def is_french_financed(allocation: dict[str, float]) -> bool:
        """
        Return True if France is the biggest single contributor to the film's budget.
        
        Args:
            allocation (dict): A dict mapping country names to their budget share (e.g. {'France': 40, 'Germany': 30})

        Returns:
            bool: True if France has the highest share or is tied for highest.
        """
        if not allocation:
            return False

        france_share = allocation.get("France", 0)
        max_share = max(allocation.values(), default=0)

        return france_share == max_share

    @staticmethod
    def broadcasters(paying: list[str], free: list[str]) -> str:
        """
        Combine and format paying and free broadcasters into a clean, comma-separated string.

        Args:
            paying (list[str]): List of paying broadcasters
            free (list[str]): List of free broadcasters

        Returns:
            str: Comma-separated broadcaster names, e.g. "M6, TF1"
        """
        all_broadcasters = paying + free
        cleaned = sorted(set(b.strip() for b in all_broadcasters if isinstance(b, str)))
        return ", ".join(cleaned)
    
    def genre_categories(genre_names: list[str]) -> str | None:
        """
        Return a comma-separated string of high-level genre categories 
        derived from a list of raw genre names.

        Args:
            genre_names (list[str]): raw genre names (e.g. ['Drame', 'Documentaire'])

        Returns:
            str | None: e.g. 'Drame, Documentaire', or None if no known categories
        """
        cleaned = [g.strip() for g in genre_names if g]
        mapped_categories = {
            GENRE_CATEGORIES[g.lower()]
            for g in cleaned
            if g.lower() in GENRE_CATEGORIES
        }

        return ", ".join(sorted(mapped_categories)) if mapped_categories else None
