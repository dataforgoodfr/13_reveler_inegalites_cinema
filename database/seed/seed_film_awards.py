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
)

def seed_film_awards(filename):
    session = SessionLocal()

    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            rows = list(csv.DictReader(csvfile))
            for row in tqdm(rows, total=len(rows), desc="Processing"):
                film_title = row['title']
                film_director = row['director']
                country_name = row['country']
                festival_name = row['festival']
                year = int(row['year'])
                distinction = row['distinction']
                reward = row['reward']

                country = country_repository.find_or_create_country(session, country_name)

                film = film_repository.find_most_similar_film_by_director(session, film_title, film_director)
                if not film:
                    continue

                # Contribution of a country to a film (100% by default)
                allocation_null = float(100)
                film_country_budget_allocation_repository.find_or_create_budget_allocation(session, film.id, country.id, allocation_null)
                    
                festival = festival_repository.find_or_create_festival(session, country.id, festival_name, "", "")
                    
                festival_award = festival_award_repository.insert_festival_award(session, reward, festival.id)

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
