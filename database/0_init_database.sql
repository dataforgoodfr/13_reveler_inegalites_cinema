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
    devis INTEGER,
    genre TEXT,
    bonus_parite BOOLEAN,
    femme_realisatrice BOOLEAN,
    -- tmdb_id,
    -- imdb_id,
    -- tmbd_note_moyenne
    -- tmdb_total_votes
    -- tmdb_score
    -- description
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

CREATE TABLE inegalites_cinema.genres (
    id SERIAL PRIMARY KEY,
    genre TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

drop table if exists inegalites_cinema.cheffes_postes cascade;
CREATE TABLE inegalites_cinema.cheffes_postes (
    id SERIAL PRIMARY KEY,
    type_de_poste TEXT,
    nom TEXT,
    genre TEXT,
    nom2 TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inegalites_cinema.film_festival (
    id_film INTEGER,
    id_festival INTEGER,
--    PRIMARY KEY (id_film, id_festival),
    FOREIGN KEY (id_film) REFERENCES film(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_festival) REFERENCES festival(id) ON DELETE CASCADE ON UPDATE CASCADE
);

drop table if exists inegalites_cinema.film_cheffes_postes cascade;
CREATE TABLE inegalites_cinema.film_cheffes_postes (
    id_film INTEGER,
    id_cheffes_postes INTEGER,
    PRIMARY KEY (id_film, id_cheffes_postes),
    FOREIGN KEY (id_film) REFERENCES film(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_cheffes_postes) REFERENCES cheffes_postes(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE inegalites_cinema.film_genres (
    id_film INTEGER,
    id_genre INTEGER,
    PRIMARY KEY (id_film, id_genre),
    FOREIGN KEY (id_film) REFERENCES film(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_genre) REFERENCES genres(id) ON DELETE CASCADE ON UPDATE CASCADE
);