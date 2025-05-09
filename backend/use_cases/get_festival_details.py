from sqlalchemy.orm import Session
from backend.repositories import festival_repository, festival_award_repository, award_nomination_repository, film_repository
from backend.use_cases import get_film_details
from backend.services import festival_metrics_calculator
from database.models import Festival

class GetFestivalDetails:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, festival_id: int, year: int | None=None, award_id: int | None=None):
        # Get festival
        festival = festival_repository.get_festival(self.db, festival_id)
        if not festival:
            return {"error": "Festival not found"}

        # Get available year
        years_with_awards = award_nomination_repository.get_years_with_awards(self.db, festival.id)
        if not years_with_awards:
            return {"error: No award nomination found for this festival"}

        # Determine year
        if year is None:
            year = max(years_with_awards)
        if year not in years_with_awards:
                return {"error": "No award nomination found for this festival"}

        # Get awards for that year
        print("type(year)")
        print(type(year))
        festival_awards = festival_award_repository.get_festival_awards_by_id_year(self.db, festival.id, str(year))
        if not festival_awards:
            return {"error": f"No awards found for year {year}"}

        # Determine specific award
        selected_award = None
        if award_id:
            selected_award = next((a for a in festival_awards if a.id == award_id), None)
            if not selected_award:
                return {"error": f"Award ID {award_id} not found for year {year}"}
        else:
            selected_award = festival_awards[0]

        # Get nomination data for selected award
        nomination_data = self._get_nomination_data(selected_award.id)
        award_data = {
            "award_id": selected_award.id,
            "name": selected_award.name,
            "nominations": nomination_data
        }

        # Get festival data
        festival_data = self._get_festival_data(festival, year)

        # Get available awards list
        available_awards = [
        {
            "award_id": award.id,
            "name": award.name
        }
        for award in festival_awards
        ]

        return {
            "festival": festival_data,
            "year": year,
            "available_years": years_with_awards,
            "award": award_data,
            "available_awards": available_awards
        }

    def _get_nomination_data(self, award_id: int):
        nominations = award_nomination_repository.get_award_nominations_by_award_id(self.db, award_id)
        nomination_data = []
        for nomination in nominations:
            film = get_film_details.GetFilmDetails(self.db).execute(nomination.film_id)
            film_summary = {
                "id": film["id"],
                "original_name": film["original_name"],
                "release_date": film["release_date"],
                "poster_image_base64": film["poster_image_base64"],
                "director": film_repository.get_individual_directors_for_film(self.db, film["id"]),
                "female_representation_in_key_roles": film["metrics"]["female_representation_in_key_roles"],
                "female_representation_in_casting": film["metrics"]["female_representation_in_casting"],
            } 
            
            nomination_data.append({
                "nomination_id": nomination.id,
                "date": nomination.date.isoformat() if nomination.date else None,
                "is_winner": nomination.is_winner,
                "film": film_summary
            })
        
        return nomination_data
   
    def _get_festival_data(self, festival: Festival, year: str):
        female_representation_in_nominated_films = festival_metrics_calculator.calculate_female_representation_in_nominated_films(self.db, festival.id, year)
        female_representation_in_winner_price = festival_metrics_calculator.calculate_female_representation_in_winner_price(self.db, festival.id, year)

        return {
            "id": festival.id,
            "name": festival.name,
            "description": festival.description,
            "date": year,
            "image_base64": festival.image_base64 if festival.image_base64 else None,
            "festival_metrics": {
                "female_representation_in_nominated_films": female_representation_in_nominated_films,
                "female_representation_in_winner_price": female_representation_in_winner_price
            }
        }