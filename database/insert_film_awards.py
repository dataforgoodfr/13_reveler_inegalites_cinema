import datetime
import logging
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import dotenv
import os
from backend.repositories import (
    festival_award_repository,
    country_repository,
    award_nomination_repository,
    film_country_budget_allocation_repository,
    film_repository,
    festival_repository,
)


dotenv.load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def import_csv(filename):
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                film_title = row['title']
                country_name = row['country']
                festival_name = row['festival']
                year = int(row['year'])
                distinction = row['distinction']
                reward = row['reward']

                country = country_repository.find_or_create_country(session, country_name)

                film = film_repository.find_or_create_film(session, film_title)

                allocation_null = float(0)
                film_country_budget_allocation_repository.find_or_create_budget_allocation(session, film.id, country.id, allocation_null)
                    
                festival = festival_repository.find_or_create_festival(session, country.id, festival_name, "", "")
                    
                festival_award = festival_award_repository.insert_festival_award(session, reward, festival.id)

                # Determine whether the award is a winner
                is_winner = distinction == "Lauréat" 
                award_nomination_repository.find_or_create_award_nomination(session, film.id, festival_award.id, is_winner, datetime.date(year, 1, 1))
                if i % 1000 == 0:
                    print(f"Processed {i} rows...")

            session.commit()
            print("Import completed successfully!")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        session.rollback()  # Rollback the transaction if an error occurs

# Run the script
if __name__ == "__main__":
    file_path = "./database/data/mubi/films_all_awards.csv"
    import_csv(file_path)
