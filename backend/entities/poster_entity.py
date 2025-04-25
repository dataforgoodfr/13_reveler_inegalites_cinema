class PosterEntity:
    def __init__(self, poster_model):
        self._model = poster_model  # wraps the ORM model

    @property
    def characters(self):
        return self._model.characters if self._model else None

    def female_average_ratio_on_poster(self) -> float | None:
        if not self.characters:
            return None

        female_characters = [
            c for c in self.characters
            if c.gender and c.gender.lower() == "female"
            and isinstance(getattr(c, "poster_percentage", None), (int, float))
        ]

        if not female_characters:
            return 0

        total = sum(c.poster_percentage for c in female_characters)
        return total * 100.0 / len(female_characters)


    def non_white_average_ratio_on_poster(self) -> float | None:
        if not self.characters:
            return None

        non_white_characters = [
            c for c in self.characters
            if c.ethnicity and c.ethnicity.lower() != "white"
            and isinstance(getattr(c, "poster_percentage", None), (int, float))
        ]

        if not non_white_characters:
            return 0

        total = sum(c.poster_percentage for c in non_white_characters)
        return total * 100.0 / len(non_white_characters)