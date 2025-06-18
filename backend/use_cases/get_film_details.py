from sqlalchemy.orm import Session, selectinload
from database.models import Film, FilmCredit, AwardNomination, FestivalAward, FilmCountryBudgetAllocation
from backend.services.film_metrics_calculator import FilmMetricsCalculator
from backend.entities.credit_holder_entity import CreditHolderEntity
from backend.entities.trailer_entity import TrailerEntity
from backend.entities.poster_entity import PosterEntity

class GetFilmDetails:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, film_id: int) -> dict:
        # Eagerly load the film with its related data
        film = self.db.query(Film).options(
            # Film credits with roles and credit holders
            selectinload(Film.film_credits)
                .selectinload(FilmCredit.role),
            selectinload(Film.film_credits)
                .selectinload(FilmCredit.credit_holder),

            # Award nominations with award and festival
            selectinload(Film.award_nominations)
                .selectinload(AwardNomination.festival_award)
                .selectinload(FestivalAward.festival),

            # Country budget allocations with related country and allocation
            selectinload(Film.country_budget_allocations)
                .selectinload(FilmCountryBudgetAllocation.country),

            # Genres (typically many-to-many)
            selectinload(Film.genres)
        ).get(film_id)

        if not film:
            return None

        film_attributes_displayed = [
            "id", "original_name", "release_date",
            "parity_bonus", "cnc_agrement_year", "budget"
        ]

        # Get the film basic details
        film_data = {
            attr: getattr(film, attr)
            for attr in film_attributes_displayed
            if hasattr(film, attr)
        }

        # Get the film duration in correct format
        if film.duration_minutes is not None:
            hours = film.duration_minutes // 60
            minutes = film.duration_minutes % 60
            film_data["duration"] = f"{hours}h{minutes:02d}"
        else:
            film_data["duration"] = None

        # Get the film genres
        film_data["genres"] = [genre.name.capitalize() for genre in film.genres]

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
        film_data["credits"] = {
            "casting": [],
            "key_roles": [],
            "distribution": [],
        }

        for credit in film.film_credits:
            holder = CreditHolderEntity(credit.credit_holder)
            role = credit.role

            credit_info = {
                "role": role.name if role else None,
                "is_key_role": role.is_key_role if role else None,
                "is_company": holder.is_company() if holder else None,
                "name": holder.full_name() if holder else None,
                "gender": credit.credit_holder.gender
            }

            # Casting: role == 'actor'
            if role and role.name == "actor":
                film_data["credits"]["casting"].append(credit_info)

            # Key roles: is_key_role == True
            if role and role.is_key_role:
                film_data["credits"]["key_roles"].append(credit_info)

            # Distribution: role in ['production_company', 'distribution_company']
            if role and role.name in ["production_company", "distribution_company"]:
                film_data["credits"]["distribution"].append(credit_info)

        # Get the film awards
        film_data["awards"] = []
        for nomination in film.award_nominations:
            award = nomination.festival_award
            festival = award.festival if award else None
            film_data["awards"].append({
                "festival_id": festival.id if festival else None,
                "festival_name": festival.name if festival else None,
                "award_name": award.name if award else None,
                "date": nomination.date.isoformat() if nomination.date else None,
                "is_winner": nomination.is_winner,
            })

        # Get the film key metrics
        metrics = FilmMetricsCalculator(film)
        trailer = TrailerEntity(film.trailer[0] if film.trailer else None)
        poster = PosterEntity(film.poster[0] if film.poster else None)
        film_data["metrics"] = {
            # Get the film main metrics
            "female_representation_in_key_roles": metrics.calculate_female_representation_in_key_roles(),
            "female_representation_in_casting": metrics.calculate_female_representation_in_casting(),
            # Get the film trailer metrics
            "female_screen_time_in_trailer": trailer.female_screen_time(),
            "non_white_screen_time_in_trailer": trailer.non_white_screen_time(),
            # Get the film poster metrics
            "female_visible_ratio_on_poster": poster.female_average_ratio_on_poster(),
            "non_white_visible_ratio_on_poster": poster.non_white_average_ratio_on_poster()
        }

        return film_data
