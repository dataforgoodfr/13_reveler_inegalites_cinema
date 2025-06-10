import pandas as pd
from tqdm import tqdm
from database.database import SessionLocal
from backend.repositories import (
    film_repository,
    poster_repository,
    poster_character_repository
)

def seed_poster_predictions():
    df = pd.read_csv("database/data/predictions_on_posters.csv")

    session = SessionLocal()
    try:
        with session.begin():
            for _, row in tqdm(df.iterrows(), total=len(df), desc="Seeding poster predictions"):
                visa_number = row["visa_number"]

                # Étape 1 : Récupérer le film via visa_number
                film = film_repository.find_film_by_visa(session, visa_number)
                if not film:
                    print(f"Film introuvable pour visa_number {visa_number}")
                    continue

                # Étape 2 : Récupérer le poster via film_id
                poster = poster_repository.find_poster_by_film_id(session, film.id)
                if not poster:
                    print(f"Poster introuvable pour film_id {film.id}")
                    continue

                # Étape 3 : Préparer les données de prédiction
                predictions_data = {
                    "gender": row["gender"],
                    "age_min": row["age_min"],
                    "age_max": row["age_max"],
                    "ethnicity": row["ethnicity"],
                    "poster_percentage": row["poster_percentage"]
                }

                # Étape 4 : Créer ou mettre à jour le PosterCharacter
                poster_character_repository.create_or_update_poster_character(
                    session, poster.id, predictions_data
                )

            session.commit()
            print(f"Seeded {len(df)} poster predictions.")
    except Exception as e:
        session.rollback()
        print("Error while seeding poster predictions:", e)
    finally:
        session.close()

if __name__ == "__main__":
    seed_poster_predictions()
