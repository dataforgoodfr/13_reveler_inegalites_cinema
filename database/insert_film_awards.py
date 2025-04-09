# from pathlib import Path
# from database import SessionLocal
import datetime
import logging
from database.models import Country
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
            for row in reader:
                film_title = row['title']
                director_name = row['director']
                country_name = row['country']
                link = row['link']
                festival_name = row['festival']
                year = int(row['year'])
                distinction = row['distinction']
                reward = row['reward']

                # to check if "film award" CSV column exist, get festival award by name and join with festival name
                f = festival_award_repository.get_festival_award_by_name(session, festival_name, reward)
                print(f)
                if not f:
                    country = country_repository.find_or_create_country(session, country_name)
                    
                    film = film_repository.find_or_create_film(session, film_title)
                    
                    allocation_null = float(0)
                    film_country_budget_allocation_repository.find_or_create_budget_allocation(session, film.id, country.id, allocation_null)
                    
                    festival = festival_repository.find_or_create_festival(session, country.id, film_title, "", "")
                    
                    festival_award = festival_award_repository.insert_festival_award(session, reward, festival.id)
                    
                    # Determine whether the award is a winner
                    is_winner = True if distinction == "Lauréat" else False 
                    award_nomination_repository.find_or_create_award_nomination(session, film.id, festival_award.id, is_winner, datetime.date(year, 1, 1))
            session.commit()            
    except Exception as e:
        logging.error(f"An error occurred during CSV import: {e}")
        session.rollback()  # Rollback the transaction if an error occurs
# Run the script
if __name__ == "__main__":
    file_path = "./database/data/mubi/films_all_awards.csv"
    import_csv(file_path)
