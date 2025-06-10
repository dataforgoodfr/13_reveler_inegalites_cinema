import pandas as pd
from tqdm import tqdm
from database.database import SessionLocal
from backend.repositories import (
    film_repository,
    trailer_repository,
    trailer_character_repository
)

def seed_trailer_predictions():
    df = pd.read_csv("database/data/predictions_on_posters.csv")

    session = SessionLocal()
    try:
        with session.begin():
            for _, row in tqdm(df.iterrows(), total=len(df), desc="Seeding poster predictions"):
                visa_number = row["visa_number"]

                # Étape 1 : récupérer le film à partir du visa_number
                film = film_repository.find_film_by_visa(session, visa_number)
                if not film:
                    print(f"Film non trouvé pour visa {visa_number}")
                    continue

                # Étape 2 : récupérer le trailer lié au film
                trailer = trailer_repository.find_trailer_by_film_id(session, film.id)
                if not trailer:
                    print(f"Trailer non trouvé pour film_id {film.id}")
                    continue

                predictions_data = {
                    "gender": row["gender"],
                    "age_min": row["age_min"],
                    "age_max": row["age_max"],
                    "ethnicity": row["ethnicity"],
                    "time_on_screen": row.get("time_on_screen"),  # si dispo
                    "average_size_on_screen": row.get("average_size_on_screen"),  # si dispo
                }

                # Étape 3 : créer ou mettre à jour trailer_character
                trailer_character_repository.create_or_update_trailer_character(
                    session, trailer.id, predictions_data
                )

            session.commit()
            print(f"Seeded {len(df)} poster predictions.")
    except Exception as e:
        session.rollback()
        print("Error while seeding poster predictions:", e)
    finally:
        session.close()

if __name__ == "__main__":
    seed_trailer_predictions()
