import pandas as pd
from tqdm import tqdm
from database.database import SessionLocal
from backend.repositories import (
    film_repository,
    #film_trailer_repository  
)

#Importation des résultats de la ML squr trailer dans la bdd

def seed_trailer_predictions():
    df = pd.read_csv("database/data/predictions_on_trailers.csv")

    session = SessionLocal()
    try:
        with session.begin():
            for _, row in tqdm(df.iterrows(), total=len(df), desc="Seeding trailer demographics"):
                visa_number = row["visa_number"]
                if film_repository.find_film_by_visa(session, visa_number) is not None:
                    continue  # Skip if already seeded

                prediction_data = {
                    "visa_number": row["visa_number"],
                    "allocine_id": row["allocine_id"],
                    "gender": row["gender"],
                    "age_min": row["age_min"],
                    "age_max": row["age_max"],
                    "ethnicity": row["ethnicity"],
                    "time_on_screen": row["time_on_screen"],
                    "average_size_on_screen": row["average_size_on_screen"]
                }

                #film_prediction_repository.create_or_update_prediction(session, prediction_data)
            session.commit()
            print(f"Seeded {len(df)} trailer predictions.")
    except Exception as e:
        session.rollback()
        print("Error while seeding trailer predictions:", e)
    finally:
        session.close()

if __name__ == "__main__":
    seed_trailer_predictions()
