# Data For Good #13 - Révéler les Inégalités dans le Cinéma (RIC) - Documentation Backend

## Comment lancer le backend ?

Pour lancer le backend seul
* Builder le container: `docker build -t my-backend . -f backend/Dockerfile`
* Lancer le container: `docker run -p 5001:5001 --rm my-backend`
* Ouvrir un navigateur et se rendre à cette url: `http://localhost:5001/`

Pour lancer le backend avec la base de données
* Builder et lancer les containers: `docker-compose up --build`
* Ouvrir un navigateur et se rendre à cette url: `http://localhost:5001/`

## Comment manipuler les données ?

Nous utilisons l'ORM [SQLAlchemy](https://docs.sqlalchemy.org/en/20/) pour manipuler avec Python les données de la base de données.

### Étape 1 : Créer une session pour interragir avec la base de données
Toute interaction avec la base de données nécessite de créer une session qui agit comme connection temporaire.
Le fichier `database/database.py` agit comme configuration de base pour créer des sessions.
Deux options sont possibles :
* Option 1: au sein du framework FastAPI
    ```
    from fastapi import FastAPI, Depends
    from sqlalchemy.orm import Session
    from database import get_db
    from models import Film

    app = FastAPI()

    @app.get("/films/{film_name}")
    def get_film(film_name: str, db: Session = Depends(get_db)):
        film = db.query(Film).filter_by(name=film_name).first()
        return {"film": film}
    ```

* Option 2 : hors du framework FastAPI (pour les scripts d'import de données python) 
    ```
    from database import SessionLocal
    from models import Film  # Assuming your Film model is in models.py

    session = SessionLocal()
    try:
        film = session.query(Film).filter_by(name="Le Comte de Monte-Cristo").first()
        print(film)
    finally:
        session.close()
    ```

### Étape 2 : liste de commandes simples pour récupérer, créer, mettre à jour, supprimer des données
Voici une liste non exhaustive de commandes simples à exécuter sur la tables `films` :
* Accéder à tous les films :
    `all_films = session.query(Film).all()`
* Accéder à un film par nom : 
    `film = session.query(Film).filter_by(name="Le Comte de Monte-Cristo").first()`
* Filtrer des films (ex par date de sortie): 
    `films_2022 = session.query(Film).filter(Film.release_date.between(date(2022, 1, 1), date(2022, 12, 31))).all()`
* Créer un nouveau film avec des attributs :
    ```
    from datetime import date
    new_film = Film(name="La jeune fille en feu", release_date=date(2019, 9, 18))
    session.add(new_film)
    session.commit()
    ```
* Mettre à jour un film :
    ```
    film = session.query(Film).filter_by(name="Le Comte de Monte-Cristo").first()
    if film:
        film.release_date = date(2023, 4, 5)  # Example new release date
        session.commit()
    ```
* Supprimer un film :
    ```
    film = session.query(Film).filter_by(name="La jeune fille en feu").first()
    if film:
        session.delete(film)
        session.commit()
    ```

## 📦 `routers/`

Tous les points d'entrée HTTP (routes) sont définis dans le dossier `routers/`.  
Chaque fichier regroupe les routes selon une logique métier, par exemple :

- `routers/films.py` → toutes les routes liées aux films

Les routes sont définies à l’aide du `APIRouter` de FastAPI et sont ensuite incluses dans l’application principale via `main.py`.

## ⚙️ `use_cases/`

La logique métier est isolée dans des classes dédiées appelées "use cases", situées dans le dossier `use_cases/`.  
Chaque use case encapsule une opération spécifique, ce qui permet de garder les handlers de routes simples et lisibles.

Par exemple :
- `GetFilmDetails` dans `use_cases/get_film_details.py` contient toute la logique nécessaire pour récupérer les informations détaillées d’un film.
