from sqlalchemy.orm import Session
from database.models import Film
from backend.services.film_metrics_calculator import FilmMetricsCalculator

class GetFilmDetails:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, film_id: int) -> dict:
        film = self.db.query(Film).filter(Film.id == film_id).first()
        if not film:
            return None

        # TODO: after demo, remove first_language, it will be replaced by list of countries_sorted_by_budget
        film_attributes_displayed = [
            "id", "original_name", "release_date", "duration",
            "first_language", "parity_bonus", "cnc_agrement_year", "budget"
        ]

        # Get the film basic details
        film_data = {
            attr: getattr(film, attr)
            for attr in film_attributes_displayed
            if hasattr(film, attr)
        }

        # Get the film genres
        film_data["genres"] = [genre.name for genre in film.genres]

        # Get the film poster and trailer
        film_data["poster_image_base64"] = film.poster[0].image_base64 if film.poster else None
        film_data["trailer_url"] = film.trailer[0].url if film.trailer else None

        # Get the film countries by order of budget invested
        allocations = [
            alloc for alloc in film.country_budget_allocations
            if alloc.budget_allocation is not None and alloc.country is not None
        ]
        sorted_allocations = sorted(allocations, key=lambda a: a.budget_allocation, reverse=True)
        film_data["countries_sorted_by_budget"] = [alloc.country.name for alloc in sorted_allocations]

        # Get the film credits
        film_data["credits"] = []
        for credit in film.film_credits:
            holder = credit.credit_holder
            role = credit.role
            film_data["credits"].append({
                "role": role.name if role else None,
                "is_key_role": role.is_key_role if role else None,
                "type": holder.type,
                "name": f"{holder.first_name} {holder.last_name}" if holder else None,
                "legal_name": holder.legal_name,
                "gender": holder.gender,
            })

        # Get the film awards
        film_data["awards"] = []
        for nomination in film.award_nominations:
            award = nomination.festival_award
            festival = award.festival if award else None
            film_data["awards"].append({
                "festival_name": festival.name if festival else None,
                "award_name": award.name if award else None,
                "date": nomination.date.isoformat() if nomination.date else None,
                "is_winner": nomination.is_winner,
            })

        # Get the film key metrics
        metrics = FilmMetricsCalculator(film)
        film_data["metrics"] = {
            # Get the film main metrics
            "female_representation_in_key_roles": metrics.calculate_female_representation_in_key_roles(),
            "female_representation_in_casting": metrics.calculate_female_representation_in_casting(),
            # Get the film trailer metrics
            "female_screen_time_in_trailer": metrics.calculate_female_screen_time_in_trailer(),
            "non_white_screen_time_in_trailer": metrics.calculate_non_white_screen_time_in_trailer(),
            # Get the film poster metrics
            "female_visible_ratio_on_poster": metrics.calculate_female_visible_ratio_on_poster(),
            "non_white_visible_ratio_on_poster": metrics.calculate_non_white_visible_ratio_on_poster()
        }

        return film_data
