from sqlalchemy.orm import Session
from sqlalchemy import select, func
from database.models import Film
from backend.repositories import film_repository

class SearchFilms:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, query: str, limit: int = 5) -> list[dict]:
        stmt = (
            select(Film)
            .where(func.lower(Film.original_name).ilike(f"%{query.lower()}%"))
            .order_by(func.length(Film.original_name))  # shorter titles show up first
            .limit(limit)
        )

        films = self.db.scalars(stmt).all()

        return [
            {
                "id": film.id,
                "title": film.original_name,
                "image": film.poster[0].image_base64 if film.poster else None,
                "year": film.release_date.year if film.release_date else None,
                "directors": film_repository.get_individual_directors_for_film(self.db, film.id)
            }
            for film in films
        ]
