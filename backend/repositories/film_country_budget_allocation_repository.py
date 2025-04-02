from sqlalchemy.orm import Session
from database.models import FilmCountryBudgetAllocation

def create_budget_allocation(session: Session, film_id: int, country_id: int, allocation: float) -> FilmCountryBudgetAllocation:
    allocation_record = FilmCountryBudgetAllocation(
        film_id=film_id,
        country_id=country_id,
        budget_allocation=allocation
    )
    session.add(allocation_record)
    return allocation_record
