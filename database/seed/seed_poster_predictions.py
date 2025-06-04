import pandas as pd
from tqdm import tqdm
from database.database import SessionLocal
from backend.repositories import (
    film_repository,
    film_prediction_repository  # <-- Le même repo utilisé
)

def seed_poster_predictions():
    df = pd.read_csv("database/data/predictions_on_posters.csv")

    session = SessionLocal()
    try:
        with session.begin():
            for _, row in tqdm(df.iterrows(), total=len(df), desc="Seeding poster predictions"):
                allocine_id = row["allocine_id"]
                film = film_repository.find_film_by_allocine_id(session, allocine_id)
                if film is None:
                    continue

                predictions_data = {
                    "film_id": film.id,
                    "source": "poster",
                    "gender": row["gender"],
                    "age_min": row["age_min"],
                    "age_max": row["age_max"],
                    "ethnicity": row["ethnicity"],
                    "poster_percentage": row["poster_percentage"]
                }

                film_prediction_repository.create_or_update_predictions(session, predictions_data)
            session.commit()
            print(f"Seeded {len(df)} poster predictions.")
    except Exception as e:
        session.rollback()
        print("Error while seeding poster predictions:", e)
    finally:
        session.close()

if __name__ == "__main__":
    seed_poster_predictions()
