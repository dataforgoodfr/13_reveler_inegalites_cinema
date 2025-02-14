-- POSTGRESQL 17
DROP SCHEMA IF EXISTS inegalites_cinema CASCADE;
CREATE SCHEMA inegalites_cinema;

SET search_path TO inegalites_cinema;


CREATE TABLE inegalites_cinema.film (
    id SERIAL PRIMARY KEY,
    nom_originel text NOT NULL,
    date_sortie_france DATE,
    pays TEXT, 
    duree INTEGER,
    langue_principale TEXT,
    format TEXT,
    n_visa_exploitation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE inegalites_cinema.realisateur (
    id SERIAL PRIMARY KEY,
    nom TEXT,
    date_naissance DATE,
    date_deces DATE,
    pays TEXT,
    genre TEXT,  
    film_genre TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inegalites_cinema.producteur (
    id SERIAL PRIMARY KEY,
    nom TEXT,
    date_naissance DATE,
    date_deces DATE,
    pays TEXT,
    genre TEXT,  
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inegalites_cinema.distributeur (
    id SERIAL PRIMARY KEY,
    nom TEXT,
    pays TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE inegalites_cinema.festival (
    id SERIAL PRIMARY KEY,
    nom TEXT,
    pays TEXT,
    ville TEXT,
    nom_du_prix text,
    premiere_edition smallint,
    mois text,
    genre text,
    description text, 
    url text,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inegalites_cinema.cheffes_postes (
    id_film INTEGER REFERENCES film(id),
    intitule_poste TEXT,
    nom TEXT,
    genre TEXT,
    visa TEXT,
    genre_film TEXT,
    bonus_parite BOOLEAN,
    is_realisateur BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_film, intitule_poste)
);

CREATE TABLE inegalites_cinema.film_distributeur (
    id_film INTEGER REFERENCES film(id),
    id_distributeur INTEGER REFERENCES distributeur(id),
    PRIMARY KEY (id_film, id_distributeur)
);

CREATE TABLE inegalites_cinema.film_festival (
    id_film INTEGER REFERENCES film(id),
    id_festival INTEGER REFERENCES festival(id),
    PRIMARY KEY (id_film, id_festival)
);

CREATE TABLE inegalites_cinema.film_realisateur (
    id_film INTEGER REFERENCES film(id),
    id_realisateur INTEGER REFERENCES realisateur(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_film, id_realisateur)
);