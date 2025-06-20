from sqlalchemy.orm import Session
from backend.repositories import festival_repository, festival_award_repository, award_nomination_repository, film_repository
from backend.entities.festival_award_entity import FestivalAwardEntity
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

        # Get years with awards (sorted latest → oldest)
        years_with_awards = sorted(
            award_nomination_repository.get_years_with_awards(self.db, festival.id),
            reverse=True
        )
        if not years_with_awards:
            return {"error": "No award nomination found for this festival"}

        # Default to most recent year
        year = year or years_with_awards[0]
        if year not in years_with_awards:
            return {"error": f"No award nomination found for year {year}"}

        # Get awards for that year
        festival_awards = festival_award_repository.get_festival_awards_by_id_year(self.db, festival.id, year)
        if not festival_awards:
            return {"error": f"No awards found for year {year}"}
        
        # Select award (given or default to first)
        selected_award = next((a for a in festival_awards if a.id == award_id), None) if award_id else festival_awards[0]
        print (f"Selected award: {selected_award.id if selected_award else 'None'}, award_id: {award_id}, year: {year}")
        if not selected_award:
            return {"error": f"Award ID {award_id} not found for year {year}"}

        # Prepare response
        return {
            "festival": self._get_festival_data(festival, str(year)),
            "year": year,
            "available_years": years_with_awards,
            "award": {
                "award_id": selected_award.id,
                "name": FestivalAwardEntity(selected_award).display_name(),
                "nominations": self._get_nomination_data(selected_award.id, year)
            },
            "available_awards": [
                {"award_id": award.id, "name": FestivalAwardEntity(award).display_name()}
                for award in festival_awards
            ]
        }

    def _get_nomination_data(self, award_id: int, year: int):
        nominations = award_nomination_repository.get_award_nominations_by_award_id(self.db, award_id, year)
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
        female_representation_in_award_winning_films = festival_metrics_calculator.calculate_female_representation_in_award_winning_films(self.db, festival.id, year)

        return {
            "id": festival.id,
            "name": festival.name,
            "description": festival.description,
            "date": year,
            "image_base64": festival.image_base64 if festival.image_base64 else None,
            "festival_metrics": {
                "female_representation_in_nominated_films": female_representation_in_nominated_films,
                "female_representation_in_award_winning_films": female_representation_in_award_winning_films
            }
        }
