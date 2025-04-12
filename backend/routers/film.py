from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.use_cases.get_film_details import GetFilmDetails
from backend.use_cases.search_films import SearchFilms
from database.database import get_db

router = APIRouter()

get_db_dep = Depends(get_db)

@router.get("/films/{film_id}")
def get_film(film_id: int, db: Session = get_db_dep):
    use_case = GetFilmDetails(db)
    film_data = use_case.execute(film_id)

    if not film_data:
        raise HTTPException(status_code=404, detail="Film not found")

    return {"film": film_data}


@router.get("/search")
def search_films(q: str = Query(..., min_length=1), db: Session = get_db_dep):
    use_case = SearchFilms(db)
    return use_case.execute(query=q)