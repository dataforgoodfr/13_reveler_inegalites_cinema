from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from database.models import Role
from backend.utils.name_utils import remove_extra_spaces
from backend.constants.role_constants import ROLES

def find_or_create_role(session: Session, name: str = None, allocine_name: str = None) -> Role:
    if not name and not allocine_name:
        raise ValueError("You must provide at least one of 'name' or 'allocine_name'")

    name = remove_extra_spaces(name).lower() if name else None
    allocine_name = remove_extra_spaces(allocine_name) if allocine_name else None

    filters = []
    if name:
        filters.append(Role.name == name)
    if allocine_name:
        filters.append(func.lower(Role.allocine_name) == allocine_name.lower())

    role = session.query(Role).filter(or_(*filters)).first()

    if not role:
        matched_data = None
        for entry in ROLES:
            if name and entry.get("name").lower() == name:
                matched_data = entry
                break
            elif allocine_name and remove_extra_spaces(entry.get("allocine_name", "")) == allocine_name:
                matched_data = entry
                break
        if not matched_data:
            print(f"Role not found for name: {name} or allocine_name: {allocine_name}")
            raise ValueError("Role not found in predefined constants")

        role = Role(
            name=matched_data.get("name").lower(),
            allocine_name=matched_data.get("allocine_name"),
            is_key_role=matched_data.get("key_role", False),
            inclusive_name=matched_data.get("inclusive_name", None),
        )

        session.add(role)
        session.flush()

    return role
