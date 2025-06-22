from tqdm import tqdm
import datetime
import logging
import csv
from database.database import SessionLocal
from backend.repositories import (
    festival_award_repository,
    country_repository,
    award_nomination_repository,
    film_country_budget_allocation_repository,
    film_repository,
    festival_repository,
    role_repository,
    credit_holder_repository,
    film_credit_repository
)

def seed_film_awards(filename):
    session = SessionLocal()

    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            rows = list(csv.DictReader(csvfile))
            director_role = role_repository.find_role_by_name(session, "director")
            for row in tqdm(rows, total=len(rows), desc="Processing"):
                film_title = row['title']
                film_director = row['director']
                country_name = row['country']
                festival_name = row['festival']
                year = int(row['year'])
                distinction = row['distinction']
                mubi_label = row['reward']

                country = country_repository.find_or_create_country(session, country_name)

                film = film_repository.find_most_similar_film_by_director(session, film_title, film_director)
                if not film:
                    film = film_repository.create_film(session, { "original_name": film_title })
                    credit_holder = credit_holder_repository.find_or_create_credit_holder(session, film_director, "Individual")
                    if not credit_holder:
                        print(f"Credit holder not found or created for {film_director}")
                        continue
                    film_credit_repository.find_or_create_film_credit(
                        session,
                        film_id=film.id,
                        role_id=director_role.id,
                        credit_holder_id=credit_holder.id
                    )

                # Contribution of a country to a film (100% by default)
                allocation_null = float(100)
                film_country_budget_allocation_repository.find_or_create_budget_allocation(session, film.id, country.id, allocation_null)
                    
                festival = festival_repository.find_or_create_festival(session, festival_name)
                if not festival:
                    continue
                
                festival_award = festival_award_repository.find_or_create_festival_award(session, festival.id, mubi_label)
                if not festival_award:
                    continue

                # Determine whether the award is a winner
                is_winner = distinction == "Lauréat" 
                award_nomination_repository.find_or_create_award_nomination(session, film.id, festival_award.id, is_winner, datetime.date(year, 1, 1))

            session.commit()
            print("Import completed successfully!")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        session.rollback()  # Rollback the transaction if an error occurs
    finally:
        session.close()

# Run the script
if __name__ == "__main__":
    file_path = "./database/data/mubi/films_all_awards.csv"
    seed_film_awards(file_path)
