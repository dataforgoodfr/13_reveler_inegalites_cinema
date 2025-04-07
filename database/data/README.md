## EXTRACTING DATA FROM EXTERNAL SOURCES

## 🎬 MUBI Festival & Awards Scraper

This project scrapes film data from [MUBI](https://mubi.com) with a focus on major festival listings and award data for selected films.

### 🧩 Step 1 — Festival Film Scraper (`MubiAllFestivalFilmsToCsv`)

Scrapes all the films from the following MUBI festival pages:
- **Oscars** (Academy Awards)
- **Césars** (French National Film Awards)

For each **year between 2010 and 2024**, the scraper collects:
- Festival name
- Festival year edition
- Film title
- Film director
- Film country
- Film nominations (optional)
All results are stored in a single **CSV file**.

### 🧩 Step 2 — Award Scraper (`MubiAllFilmAwardsToCsv` or similar)

Using the list of films from step 1, this scraper:
- Visits each **film’s MUBI page**
- Collects from step 1 the following fields
  - Film name
  - Film director
  - Film country
  - Festival
  - Festival year edition 
- Extracts all **awards and nominations**
  - Award name
  - Distinction
All results are stored in a single **CSV file**.

#### ▶️ How to Run

```bash
# Run step 1 — Scrape all festival films
python database/data/mubi/mubi_all_festival_films_to_csv.py --festival festival --start_year 2010 --end_year 2024

# Run step 2 — Enrich films with award data
python database/data/mubi/mubi_all_film_awards_to_csv.py
```

---

## 🎬 Allociné Scraper & Enricher

This project scrapes film data from [Allociné](https://www.allocine.fr) and enriches a local dataset (stored in a CSV file) with detailed metadata and casting information for each film.

It’s designed to run in two stages:
1. **Matching:** Search Allociné for each film by title/year, and store the matched Allociné ID and URL.
2. **Enrichment:** Use the Allociné ID to scrape detailed film data and casting information from two different pages.

### 🧩 Structure

#### 1. `AllocineFilmMatcher`
- Connects to your database (via SQLAlchemy)
- Loops through all films in the `films` table
- Searches Allociné using the original film name and year
- Stores the first match in `allocine_matches.csv`:
  - `film_id`
  - `original_name`
  - `cnc_agrement_year`
  - `allocine_id`
  - `allocine_title`
  - `allocine_url`

#### 2. `AllocineFilmEnricher`
- Reads `allocine_matches.csv`
- Skips already enriched films
- For each `allocine_id`, fetches:
  - **Film details** from `fichefilm_gen_cfilm=xxx.html`
  - **Casting info** from `casting_gen_cfilm=xxx.html`
- Adds enriched fields into the CSV:
  - `description`, `release_date`, `genres`, `image_url`, etc.
  - `directors`, `actors`
  - `Scénaristes`, `Production`, `Equipe technique`, `Soundtrack`, `Distribution`

### ▶️ How to Run

Use the runner script to choose which stage(s) to run.

```bash
python database/data/allocine/allocine_runner.py --matcher
python database/data/allocine/allocine_runner.py --enricher
```

Or with nohup
```bash
nohup python database/data/allocine/allocine_runner.py --matcher > output.log 2>&1 &
```