import pandas as pd
from tqdm import tqdm
from database.database import SessionLocal
from backend.repositories import (
    film_repository,
    #film_poster_characters_repository  
)

def seed_poster_predictions():
    df = pd.read_csv("database/data/predictions_on_posters.csv")

    session = SessionLocal()
    try:
        with session.begin():
            for _, row in tqdm(df.iterrows(), total=len(df), desc="Seeding poster predictions"):
                visa_number = row["visa_number"]
                if film_repository.find_film_by_visa(session, visa_number) is not None:
                    continue  # Skip if already seeded

                predictions_data = {
                    "visa_number": row["visa_number"],
                    "allocine_id": row["allocine_id"],
                    "gender": row["gender"],
                    "age_min": row["age_min"],
                    "age_max": row["age_max"],
                    "ethnicity": row["ethnicity"],
                    "poster_percentage": row["poster_percentage"]
                }

                #film_poster_characters_repository .create_or_update_predictions(session, predictions_data)
            session.commit()
            print(f"Seeded {len(df)} poster predictions.")
    except Exception as e:
        session.rollback()
        print("Error while seeding poster predictions:", e)
    finally:
        session.close()

if __name__ == "__main__":
    seed_poster_predictions()
