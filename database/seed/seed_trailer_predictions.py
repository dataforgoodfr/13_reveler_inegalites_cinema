import pandas as pd
from tqdm import tqdm
from database.database import SessionLocal
from backend.repositories import (
    film_repository,
    trailer_repository,
    trailer_character_repository
)
from backend.utils.age_utils import parse_age

DEFAULT_CSV_PATH = "database/data/machine_learning_predictions/trailer_predictions.csv"

def seed_trailer_predictions(csv_path: str = DEFAULT_CSV_PATH):
    df = pd.read_csv(csv_path)
    visa_numbers = df["visa_number"].dropna().astype(str).unique().tolist()

    session = SessionLocal()
    try:
        with session.begin():
            # Step 0: Bulk delete existing PosterCharacter records for the given visa numbers
            trailer_character_repository.bulk_delete_by_film_visas(session, visa_numbers)

            for _, row in tqdm(df.iterrows(), total=len(df), desc="Seeding trailer predictions"):
                visa_number = row["visa_number"]

                # Step 1: Get the film by visa_number
                film = film_repository.find_film_by_visa(session, visa_number)
                if not film:
                    print(f"Film not found for visa_number {visa_number}")
                    continue
                
                if str(film.visa_number) != str(visa_number):
                    print(f"Film visa number mismatch: expected {visa_number}, found {film.visa_number}")
                    continue

                # Step 2: Get the trailer for the film
                trailer = trailer_repository.find_trailer_by_film_id(session, film.id)
                if not trailer:
                    print(f"Trailer not found for film_id {film.id}")
                    continue

                # Step 3: Prepare prediction data
                prediction_data = {
                    "gender": row["gender"].strip().lower() if isinstance(row["gender"], str) else None,
                    "age_min": parse_age(row["age_min"]),
                    "age_max": parse_age(row["age_max"]),
                    "ethnicity": row["ethnicity"].strip().lower() if isinstance(row["ethnicity"], str) else None,
                    "time_on_screen": float(row["time_on_screen"]) if pd.notna(row["time_on_screen"]) else None,
                    "average_size_on_screen": float(row["average_size_on_screen"]) if pd.notna(row["average_size_on_screen"]) else None
                }

                # Step 4: Create new trailer character
                trailer_character_repository.create_trailer_character(session, trailer.id, prediction_data)

            session.commit()
            print(f"Seeded {len(df)} trailer predictions.")
    except Exception as e:
        session.rollback()
        print("Error while seeding trailer predictions:", e)
    finally:
        session.close()

if __name__ == "__main__":
    seed_trailer_predictions()
