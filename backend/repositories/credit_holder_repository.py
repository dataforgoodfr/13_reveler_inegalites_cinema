from sqlalchemy.orm import Session
from database.models import CreditHolder

def find_or_create_credit_holder(session: Session, credit_holder_data: dict) -> CreditHolder:
    holder = session.query(CreditHolder).filter_by(**credit_holder_data).first()
    if not holder:
        holder = CreditHolder(**credit_holder_data)
        session.add(holder)
        session.flush()
    return holder
