import csv
import ast
from tqdm import tqdm
from backend.utils.date_utils import parse_release_date, parse_duration

from database.database import SessionLocal
from backend.repositories import (
    film_repository,
    trailer_repository,
    poster_repository,
    genre_repository,
    credit_holder_repository,
    role_repository,
    film_credit_repository
)

CSV_PATH = 'database/data/allocine/allocine_matches_enriched.csv'

def seed():
    session = SessionLocal()
    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        rows = list(csv.DictReader(csvfile))
        for row in tqdm(rows, total=len(rows), desc="Processing"):
            if row['allocine_visa_number'] != row['visa_number']:
                continue

            film = film_repository.find_film_by_visa(session, row['visa_number'])
            if not film:
                continue

            # Update film basic info
            film.release_date = parse_release_date(row['release_date'])
            film.duration_minutes = parse_duration(row['duration'])

            # Trailer
            if row['trailer_url']:
                trailer_repository.create_or_update_trailer(session, film.id, row['trailer_url'])

            # Poster
            if row['poster_url']:
                poster_repository.create_or_update_poster(session, film.id, row['poster_url'])

            # Genres
            try:
                genres = eval(row['genres']) if row['genres'] else []
                for genre_name in genres:
                    genre = genre_repository.find_or_create_genre(session, genre_name)
                    if genre not in film.genres:
                        film.genres.append(genre)
            except Exception:
                print(f"Error parsing genres for film {film.id}: {row['genres']}")
                pass

            # Define how to process each credit source
            credit_sources = [
                # column, holder_type, role_type, is_list_of_dicts, fixed_role_name
                ('Casting', 'Individual', 'name', False, 'actor'),
                ('Direction', 'Individual', 'name', False, 'director'),
                ('Scénaristes', 'Individual', 'allocine_name', True, None),
                ('Production', 'Individual', 'allocine_name', True, None),
                ('Equipe technique', 'Individual', 'allocine_name', True, None),
                ('Soundtrack', 'Individual', 'allocine_name', True, None),
                ('Distribution', 'Individual', 'allocine_name', True, None),
                ('Sociétés', 'Company', 'allocine_name', True, None),
            ]

            for column, holder_type, role_key, is_dict, fixed_role in credit_sources:
                raw_value = row.get(column)
                try:
                    entries = ast.literal_eval(raw_value) if raw_value else []
                except (ValueError, SyntaxError):
                    print(f"⚠️ Failed to parse column {column}: {raw_value}")
                    continue

                for entry in entries:
                    # Normalize name and role
                    if is_dict:
                        if not isinstance(entry, dict):
                            print("⚠️ Skipping invalid dict entry :", entry)
                            continue
                        role_name = entry.get('role')
                        person_or_company_name = entry.get('name')
                        if not role_name or not person_or_company_name:
                            continue
                    else:
                        person_or_company_name = entry
                        role_name = fixed_role

                    # Get or create role
                    role = role_repository.find_or_create_role(
                        session,
                        name=role_name if role_key == 'name' else None,
                        allocine_name=role_name if role_key == 'allocine_name' else None
                    )
                    if not role:
                        print(f"Role not found for {role_name}")
                        continue

                    # Get or create credit holder
                    credit_holder = credit_holder_repository.find_or_create_credit_holder(
                        session,
                        full_name=person_or_company_name,
                        type=holder_type
                    )
                    if not credit_holder:
                        print(f"Credit holder not found for {person_or_company_name}")
                        continue

                    # Link credit
                    film_credit_repository.find_or_create_film_credit(
                        session,
                        film_id=film.id,
                        role_id=role.id,
                        credit_holder_id=credit_holder.id
                    )

        session.commit()
        session.close()

if __name__ == '__main__':
    seed()
