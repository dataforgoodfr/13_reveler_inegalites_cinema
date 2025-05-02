from sqlalchemy.orm import Session
from database.models import CreditHolder
from backend.utils.name_utils import split_full_name, guess_gender, remove_extra_spaces

def find_or_create_credit_holder(session: Session, full_name: str, type: str) -> CreditHolder:
    if not full_name or not type:
        raise ValueError("Both full_name and type are required to find or create a credit holder")
    
    full_name = remove_extra_spaces(full_name).lower()
    if type == 'Individual':
        first_name, last_name = split_full_name(full_name)
        gender = guess_gender(first_name.capitalize())
        filters = {
            'type': type,
            'first_name': first_name,
            'last_name': last_name,
            'gender': gender
        }
    elif type == 'Company':
        filters = {
            'type': type,
            'legal_name': full_name
        }
    else:
        raise ValueError("Invalid credit holder type")
    holder = session.query(CreditHolder).filter_by(**filters).first()
    if not holder:
        holder = CreditHolder(**filters)
        session.add(holder)
        session.flush()
    
    return holder