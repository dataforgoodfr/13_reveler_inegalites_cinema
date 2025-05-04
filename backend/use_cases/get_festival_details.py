from sqlalchemy.orm import Session
from backend.repositories import festival_repository, festival_award_repository, award_nomination_repository, film_repository
from backend.use_cases import get_film_details
from backend.services import festival_metrics_calculator

class GetFestivalDetails:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, festival_id: int, year: str) -> dict:
        festival = festival_repository.get_festival(self.db, festival_id)
        if not festival:
            return None

        # Get all awards linked to this festival
        festival_awards = festival_award_repository.get_festival_awards_by_festival_id(self.db, festival_id)
        
        award_data = []
        for award in festival_awards:
            nominations = award_nomination_repository.get_award_nominations_by_award_id(self.db, award.id)

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
                
            award_data.append({
                "award_id": award.id,
                "name": award.name,
                "nominations": nomination_data
            })

        nf = festival_metrics_calculator.calculate_female_representation_in_nominated_films(self.db, festival_id, year)
        wp = festival_metrics_calculator.calculate_female_representation_in_winner_price(self.db, festival_id, year)
            
        # Static festival-level metrics (TODO: add dynamic calculation later)
        festival_metrics = {
            "produced_by_women": nf,
            "prizes_awarded_to_women": wp
        }

        return {
            "festival": {
                "id": festival.id,
                "name": festival.name,
                "description": festival.description,
                "date": nomination.date.year if nomination.date else None,
                "image_base64": festival.image_base64 if festival.image_base64 else None,
                "festival_metrics": festival_metrics,
            },
            "awards": award_data
        }
        