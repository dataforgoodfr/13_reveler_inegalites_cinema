class TrailerEntity:
    def __init__(self, trailer_model):
        self._model = trailer_model  # wraps the ORM model

    @property
    def characters(self):
        return self._model.characters if self._model else None

    def female_screen_time(self) -> float | None:
        if not self.characters:
            return None

        return sum(
            c.time_on_screen
            for c in self.characters
            if c.gender and c.gender.lower() == "female"
        )

    def non_white_screen_time(self) -> float | None:
        if not self.characters:
            return None

        return sum(
            c.time_on_screen
            for c in self.characters
            if c.ethnicity and c.ethnicity.lower() != "white"
            and isinstance(c.time_on_screen, (int, float))
        )
