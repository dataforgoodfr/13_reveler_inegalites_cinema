from sqlalchemy.orm import Session
from sqlalchemy import extract
from database.models import FestivalAward, AwardNomination
from typing import List

FESTIVAL_AWARD_CONSTANTS_CSV = "backend/constants/festival_award_constants.csv"
_festival_award_constants = None  # cache

def find_or_create_festival_award(session: Session, festival_id: int, mubi_label: str) -> FestivalAward:
    constants = _load_constants()
    award_data = constants.get(mubi_label, {})

    if not award_data:
        print(f"[WARN] Festival award label not found: '{mubi_label}'")

    existing = session.query(FestivalAward).filter_by(
        mubi_label=mubi_label, festival_id=festival_id
    ).first()

    if existing:
        return existing

    festival_award = FestivalAward(
        mubi_label=mubi_label,
        french_label=award_data.get("french_label", ""),
        english_label=award_data.get("english_label", ""),
        festival_id=festival_id
    )
    session.add(festival_award)
    session.flush()
    return festival_award


def get_festival_awards_by_festival_id(session: Session, festival_id: int) -> List[FestivalAward]:
    """
    Returns a list of awards associated with a given festival.
    """
    return session.query(FestivalAward).filter_by(festival_id=festival_id).all()


def get_festival_awards_by_id_year(session: Session, festival_id: int, year: int) -> List[FestivalAward]:
    """
    Returns a list of unique awards for a given festival that have at least one nomination in the given year.
    """
    awards = (
        session.query(FestivalAward)
        .join(AwardNomination, AwardNomination.award_id == FestivalAward.id)
        .filter(
            FestivalAward.festival_id == festival_id,
            extract('year', AwardNomination.date) == year
        )
        .distinct()  # ✅ correct way to ensure uniqueness
        .order_by(FestivalAward.french_label)
        .all()
    )
    return awards

def _load_constants():
    global _festival_award_constants
    if _festival_award_constants is None:
        _festival_award_constants = {}
        with open(FESTIVAL_AWARD_CONSTANTS_CSV, mode='r', encoding='utf-8') as file:
            import csv
            reader = csv.DictReader(file)
            for row in reader:
                mubi = row['mubi_label'].strip()
                _festival_award_constants[mubi] = {
                    'english_label': row['english_label'],
                    'french_label': row['french_label'],
                }
    return _festival_award_constants
