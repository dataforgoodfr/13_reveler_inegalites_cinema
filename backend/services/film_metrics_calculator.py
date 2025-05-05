class FilmMetricsCalculator:
    def __init__(self, film):
        self.film = film
        self._categorized_roles = None  # Lazy initialization

    def _prepare_gender_data(self):
        if self._categorized_roles is not None:
            return self._categorized_roles

        key_roles = []
        actor_roles = []

        for credit in self.film.film_credits:
            role = credit.role
            holder = credit.credit_holder

            if not role or not holder or holder.type != "Individual":
                continue

            gender = holder.gender
            if gender not in ["male", "female"]:
                continue

            if role.is_key_role:
                key_roles.append(gender)

            if role.name.lower() == "actor":
                actor_roles.append(gender)

        self._categorized_roles = {
            "key_roles": key_roles,
            "actor_roles": actor_roles,
        }

    def _calculate_female_percentage(self, genders: list[str]) -> float | None:
        if not genders:
            return None
        female_count = sum(1 for g in genders if g == "female")
        return round((female_count / len(genders)) * 100, 2)

    def calculate_female_representation_in_key_roles(self) -> float | None:
        self._prepare_gender_data()
        return self._calculate_female_percentage(self._categorized_roles["key_roles"])

    def calculate_female_representation_in_casting(self) -> float | None:
        self._prepare_gender_data()
        return self._calculate_female_percentage(self._categorized_roles["actor_roles"])
