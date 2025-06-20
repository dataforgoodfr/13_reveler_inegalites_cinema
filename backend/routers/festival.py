from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from backend.use_cases.get_festival_details import GetFestivalDetails
from database.database import get_db

router = APIRouter()

get_db_dep = Depends(get_db)

@router.get("/festivals/{festival_id}")
def get_festival(
    festival_id: int,
    year: Optional[int] = Query(default=None),
    award: Optional[int] = Query(default=None),
    db: Session = get_db_dep
):
    use_case = GetFestivalDetails(db)
    festival_data = use_case.execute(festival_id, year=year, award_id=award)

    if "error" in festival_data:
        raise HTTPException(status_code=404, detail=festival_data["error"])

    return festival_data