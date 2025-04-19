from sqlalchemy.orm import Session
from database.models import Festival
from backend.repositories import festival_repository, festival_award_repository, award_nomination_repository, film_repository
from backend.use_cases import get_film_details

class GetFestivalDetails:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, festival_id: int) -> dict:
        print("festival_id: ", festival_id)
        festival = festival_repository.get_festival(self.db, festival_id)
        print(festival)
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
            
        # Static festival-level metrics (TODO: add dynamic calculation later)
        festival_metrics = {
            "parity_comparison": {
                "place": 143,
                "total": 300
            },
            "prizes_awarded_to_women": 35,
            "produced_by_women": 29
        }

        return {
            "festival": {
                "id": festival.id,
                "name": festival.name,
                "description": festival.description,
                "festival_metrics": festival_metrics,
            },
            "awards": award_data
        }
        