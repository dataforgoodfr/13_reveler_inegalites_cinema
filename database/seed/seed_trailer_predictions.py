import pandas as pd
from tqdm import tqdm
from database.database import SessionLocal
from backend.repositories import (
    film_repository,
    trailer_repository,
    trailer_character_repository
)

def seed_trailer_predictions():
    df = pd.read_csv("database/data/predictions_on_trailers.csv")  # Correct CSV name

    session = SessionLocal()
    try:
        with session.begin():
            for _, row in tqdm(df.iterrows(), total=len(df), desc="Seeding trailer predictions"):
                visa_number = row["visa_number"]

                # Step 1: Get the film by visa_number
                film = film_repository.find_film_by_visa(session, visa_number)
                if not film:
                    print(f"Film not found for visa_number {visa_number}")
                    continue

                # Step 2: Get the trailer for the film
                trailer = trailer_repository.find_trailer_by_film_id(session, film.id)
                if not trailer:
                    print(f"Trailer not found for film_id {film.id}")
                    continue

                # Step 3: Delete all existing trailer characters for this trailer
                trailer_character_repository.delete_all_by_trailer_id(session, trailer.id)

                # Step 4: Prepare prediction data
                prediction_data = {
                    "gender": str(row["gender"]).capitalize() if pd.notna(row["gender"]) else None,
                    "age_min": row["age_min"],
                    "age_max": row["age_max"],
                    "ethnicity": row["ethnicity"],
                    "time_on_screen": row.get("time_on_screen"),
                    "average_size_on_screen": row.get("average_size_on_screen"),
                }

                # Step 5: Create new trailer character
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
