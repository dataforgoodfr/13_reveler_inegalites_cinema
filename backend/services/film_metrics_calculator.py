class FilmMetricsCalculator:
    def __init__(self, film):
        self.film = film

    def calculate_female_representation_in_key_roles(self) -> float | None:
        key_roles = [
            credit for credit in self.film.film_credits
            if credit.role and credit.role.is_key_role and credit.credit_holder.type == "Individual"
        ]
        female_key_roles = [
            credit for credit in key_roles
            if credit.credit_holder and credit.credit_holder.gender == "female"
        ]
        if not key_roles:
            return None
        return round((len(female_key_roles) / len(key_roles)) * 100, 2)


    def calculate_female_representation_in_casting(self) -> float | None:
        actor_credits = [
            credit for credit in self.film.film_credits
            if credit.role and credit.role.name.lower() == "actor" and credit.credit_holder.type == "Individual"
        ]
        female_actors = [
            credit for credit in actor_credits
            if credit.credit_holder and credit.credit_holder.gender == "female"
        ]
        if not actor_credits:
            return None
        return round((len(female_actors) / len(actor_credits)) * 100, 2)


    def calculate_female_screen_time_in_trailer(self) -> float | None:
        return 30


    def calculate_non_white_screen_time_in_trailer(self) -> float | None:
        return 10
    

    def calculate_female_visible_ratio_on_poster(self) -> float | None:
        return 10


    def calculate_non_white_visible_ratio_on_poster(self) -> float | None:
        return 5
