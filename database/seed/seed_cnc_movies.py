from tqdm import tqdm # Progress bar for long-running tasks
from database.database import SessionLocal
from database.data.cnc.extract_cnc_data_from_excel import ExtractCncDataFromExcel
from backend.repositories import (
    film_repository,
    country_repository,
    film_country_budget_allocation_repository,
    film_credit_repository,
    credit_holder_repository,
    role_repository
)
from backend.entities.film_entity import FilmEntity

def seed_cnc_movies():
    """
    Seed the CNC movies into the database.
    """
    extractor = ExtractCncDataFromExcel(file_path="database/data/cnc/dataset5050_cnc_films_agrees_2003_2024.xlsx")
    data = extractor.load_data()
    data = extractor.clean_data()

    session = SessionLocal()
    try:
        with session.begin():  # starts a transaction, will rollback on error
            for _, row in tqdm(data.iterrows(), total=len(data), desc="Seeding CNC films"):
                visa_number = row["visa_number"]
                if film_repository.find_film_by_visa(session, visa_number) is not None:
                    continue  # Skip if already seeded

                film_data = {
                    "visa_number": row["visa_number"],
                    "original_name": row["original_name"],
                    "eof": row["eof"],
                    "cnc_rank": row["cnc_rank"],
                    "parity_bonus": row["parity_bonus"],
                    "asr": row["asr"],
                    "sofica_funding": row["sofica_funding"],
                    "tax_credit": row["tax_credit"],
                    "regional_funding": row["regional_funding"],
                    "cnc_agrement_year": row["cnc_agrement_year"],
                    "budget": row["budget"],
                    "budget_category": FilmEntity.budget_category(row["budget"]),
                    "is_french_financed": FilmEntity.is_french_financed(row.get("film_country_budget_allocation_rates", {})),
                    "broadcasters": FilmEntity.broadcasters(row.get("paying_broadcasters", []), row.get("free_broadcasters", []))
                }

                film = film_repository.create_film(session, film_data)

                # Creating budget allocation for each country
                for country_name, allocation in row.get("film_country_budget_allocation_rates", {}).items():
                    country = country_repository.find_or_create_country(session, country_name)
                    film_country_budget_allocation_repository.create_budget_allocation(session, film.id, country.id, allocation)

                # Adding the broadcasters to the film credits
                for broadcaster_type, role_name in [
                    ("paying_broadcasters", "paying_broadcaster"),
                    ("free_broadcasters", "free_broadcaster"),
                ]:
                    broadcasters = row.get(broadcaster_type) or []
                    role = role_repository.find_or_create_role(session, name=role_name)

                    for broadcaster_name in broadcasters:
                        holder = credit_holder_repository.find_or_create_credit_holder(session, full_name=broadcaster_name, type="Company")
                        film_credit_repository.find_or_create_film_credit(session, film.id, role.id, holder.id)
            session.commit()
            print(f"Seeded {len(data)} films.")
    except Exception as e:
        session.rollback()
        print("Error while seeding CNC movies:", e)
    finally:
        session.close()

if __name__ == "__main__":
    seed_cnc_movies()