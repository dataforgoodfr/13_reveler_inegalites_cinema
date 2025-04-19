from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.use_cases.get_festival_details import GetFestivalDetails
from database.database import get_db

router = APIRouter()

get_db_dep = Depends(get_db)

@router.get("/festivals/{festival_id}")
def get_festival(festival_id: int, db: Session = get_db_dep):
    use_case = GetFestivalDetails(db)
    festival_data = use_case.execute(festival_id)

    if not festival_data:
        raise HTTPException(status_code=404, detail="festival not found")

    return {"festival": festival_data}
