-- This file contains a sample dataset for the ric_films and genres tables.
-- WARNING: This file is not intended to be used in production.

-- Truncate all table informations
TRUNCATE TABLE
   ric_countries,
   ric_festivals,
   ric_festival_awards,
   ric_roles,
   ric_credit_holders,
   ric_genres,
   ric_films
RESTART IDENTITY CASCADE;

-- Films
INSERT INTO ric_films (
    id, original_name, visa_number, release_date, duration_minutes, first_language,
    allocine_id, budget, parity_bonus, eof, asr, sofica_funding,
    tax_credit, regional_funding, cnc_agrement_year, cnc_rank
) VALUES
-- Le Comte de Monte-Cristo
(1, 'Le Comte de Monte-Cristo', 158738, '2024-06-28', 178, 'French', 288404, 43000000, false, true, NULL, false, true, true, 2023, 3),
-- Emilia Pérez
(2, 'Emilia Pérez', 158907, '2024-11-13', 130, 'Spanish', 304508, 24990000, false, true, 'avant', false, true, true, 2023, 4),
-- Saint Omer
(3, 'Saint Omer', 146896, '2022-11-23', 123, 'French', 280206, 3260000, true, true, 'avant', true, true, true, 2021, 4),
-- L'Événement
(4, 'L''Événement', 153108, '2021-11-24', 100, 'French', 275122, 4360000, true, true, 'avant', true, true, true, 2020, 2),
-- Titane
(5, 'Titane', 148345, '2021-07-14', 108, 'French', 277192, 7430000, true, true, 'avant', true, true, true, 2020, 2);

-- Genres
INSERT INTO ric_genres (
id, name
) VALUES
(91,'historique'),
(92, 'aventure'),
(93, 'drame'),
(94, 'comédie musicale'),
(95, 'thriller'),
(96, 'judiciaire'),
(97, 'epouvante-horreur');

-- Film Genres
INSERT INTO ric_films_genres (
film_id, genre_id
) VALUES
-- Le Comte de Monte-Cristo
(1, 91),
(1, 92),
-- Emilia Pérez
(2, 93),
(2, 94),
(2, 95),
-- Saint Omer
(3, 93),
(3, 96),
-- L'Événement
(4, 93),
-- Titane
(5, 93),
(5, 95),
(5, 97);

-- Countries
INSERT INTO ric_countries (
id, name
) VALUES
(21,'France'),
(22, 'Belgique'),
(23, 'USA'),
(24, 'Europe');

-- Film Countries allocations
INSERT INTO ric_film_country_budget_allocations (
country_id, film_id, budget_allocation
) VALUES
-- Le Comte de Monte-Cristo
(21, 1, 100),
-- Emilia Pérez
(21, 2, 100),
-- Saint Omer
(21, 3, 100),
-- L'Événement
(21, 4, 100),
-- Titane
(21, 5, 90), (22, 5, 10);

-- Festivals
INSERT INTO ric_festivals (
id, name, description, image_base64, country_id
) VALUES
(1, 'César', 'Les César du cinéma sont des récompenses cinématographiques créées en 1976 et remises annuellement à Paris par l''Académie des arts et techniques du cinéma', '', 21),
(2, 'Lumières de la presse étrangère', 'Les Lumières de la presse internationale sont un ensemble de récompenses cinématographiques françaises créées en 1996 et remises annuellement à Paris par l''Académie des Lumières de la presse internationale, composée de correspondants de la presse internationale à Paris.', '', 21),
(3, 'Festival de Cannes', 'Au fil de ses éditions, le Festival de Cannes s''est imposé comme l''un des miroirs de la production cinématographique à travers le monde.', '', 21),
(4, 'Oscars', 'Les Oscars sont des récompenses cinématographiques américaines décernées chaque année depuis 1929 à Los Angeles et destinées à saluer l''excellence des productions internationales du cinéma.', '', 23),
(5, 'BAFTA Awards', 'Les BAFTA Awards sont des récompenses britanniques décernées chaque année par la British Academy of Film and Television Arts.', '', 22),
(6, 'Golden Globes', 'Les Golden Globes sont des récompenses américaines décernées chaque année par la Hollywood Foreign Press Association.', '', 23),
(7, 'Mostra de Venise', 'La Mostra de Venise est un festival international de cinéma qui se tient chaque année à Venise, en Italie.', '', 22),
(8, 'Festival International du Film de la Roche-sur-Yon', 'Festival de cinéma se tenant chaque année à La Roche-sur-Yon, en France.', '', 21),
(9, 'Festival International des Jeunes Réalisateurs de Saint-Jean-de-Luz', 'Festival mettant en avant les jeunes réalisateurs, se tenant à Saint-Jean-de-Luz, France.', '', 21),
(10, 'Directors Guild of America Awards', 'Récompenses décernées par la Directors Guild of America aux meilleurs réalisateurs.', '', 23),
(11, 'European Film Awards', 'Ces prix saluent l''excellence des œuvres et des productions européennes dans différents domaines.', '', 24),
(12, 'Fondation Gan pour le cinéma', 'La Fondation Gan pour le cinéma est une fondation du Groupe d''assurances Groupama. Créée en 1987, sous l''égide du réalisateur français Costa-Gavras, elle a vocation à soutenir la création et la diffusion de premiers longs métrages.', '', 21);


-- Festival awards
INSERT INTO ric_festival_awards (
  id, name, festival_id
) VALUES
-- César (festival_id = 1)
(11, 'Meilleure réalisation', 1),
(12, 'Meilleure musique', 1),
(13, 'Meilleur son', 1),
(14, 'Meilleure adaptation', 1),
(15, 'Meilleur film français de l''année', 1),
(16, 'Meilleure photographie', 1),
(17, 'Meilleurs effets visuels', 1),
(18, 'Meilleure actrice', 1),
(19, 'Meilleurs décors', 1),
(20, 'Meilleurs costumes', 1),
(21, 'Meilleur montage', 1),
(22, 'César de la Meilleure première œuvre', 1),
(23, 'César du Meilleur jeune espoir féminin', 1),
(24, 'César du Meilleur scénario original', 1),
(25, 'César du Meilleur acteur dans un second rôle', 1),
(26, 'César de la Meilleure actrice dans un second rôle', 1),
(27, 'César du Meilleur acteur', 1),
(28, 'César de la Meilleure musique originale', 1),
-- Lumières de la presse étrangère (festival_id = 2)
(29, 'Meilleur scénario', 2),
(30, 'Meilleure actrice', 2),
(31, 'Meilleure mise en scène', 2),
(32, 'Meilleur film', 2),
(33, 'Meilleure musique', 2),
(34, 'Meilleure image', 2),
(35, 'Lumières de la Meilleure image', 2),
(36, 'Lumières de la Révélation féminine de l''année', 2),
(37, 'Lumières du Meilleur acteur', 2),
-- Festival de Cannes (festival_id = 3)
(38, 'Prix du Jury', 3),
(39, 'Prix d''interprétation féminine', 3),
(40, 'Palme d''Or', 3),
(41, 'Longs métrages - Hors-compétition', 3),
-- Oscars (festival_id = 4)
(42, 'Meilleure actrice', 4),
(43, 'Meilleure actrice dans un second rôle', 4),
(44, 'Meilleur scénario adapté', 4),
(45, 'Meilleur son', 4),
(46, 'Meilleure chanson', 4),
(47, 'Meilleur film', 4),
(48, 'Meilleure photographie', 4),
(49, 'Meilleurs maquillages', 4),
(50, 'Meilleur réalisateur', 4),
(51, 'Meilleur montage', 4),
(52, 'Meilleure musique', 4),
(53, 'Meilleur film international', 4),
-- BAFTA Awards (festival_id = 5)
(54, 'Meilleure actrice dans un second rôle', 5),
(55, 'Meilleur film non anglophone', 5),
(56, 'Meilleure actrice', 5),
(57, 'Meilleur scénario adapté', 5),
(58, 'Meilleure chanson', 5),
(59, 'Meilleurs maquillages et coiffures', 5),
(60, 'Meilleur montage', 5),
(61, 'Meilleur film', 5),
(62, 'Meilleure réalisation', 5),
(63, 'Meilleure photographie', 5),
-- Golden Globes (festival_id = 6)
(64, 'Meilleure comédie ou comédie musicale', 6),
(65, 'Meilleure actrice dans un second rôle', 6),
(66, 'Meilleur film en langue étrangère', 6),
(67, 'Meilleure chanson', 6),
(68, 'Meilleure actrice dans une comédie ou une comédie musicale', 6),
(69, 'Meilleur réalisateur', 6),
(70, 'Meilleur scénario', 6),
(71, 'Meilleure musique', 6),
-- Mostra de Venise (festival_id = 7)
(72, 'Lion d''Argent - Grand Prix du Jury', 7),
(73, 'Lion d''Or', 7),
(74, 'Longs métrages - Compétition', 7),
-- Festival de La Roche-sur-Yon (festival_id = 8)
(75, 'Prix du public', 8),
-- Festival de Saint-Jean-de-Luz (festival_id = 9)
(76, 'Grand Prix', 9),
-- Directors Guild of America Awards (festival_id = 10)
(77, 'Meilleur réalisateur', 10),
-- European Film Awards (festival_id = 11)
(78, 'European Film Award de la Meilleure coiffure-maquillage', 11),
-- Fondation Gan pour le cinéma (festival_id = 12)
(79, 'Prix Fondation Gan', 12);


-- Award nominations
-- Insert award_nominations pour 5 films
INSERT INTO ric_award_nominations (
  id, film_id, award_id, date, is_winner
) VALUES
-- Le Comte de Monte-Cristo (film_id = 1)
(1, 1, 20, '2025-02-28', TRUE),
(2, 1, 19, '2025-02-28', TRUE),
(3, 1, 15, '2025-02-28', FALSE),
(4, 1, 25, '2025-02-28', FALSE),
(5, 1, 28, '2025-02-28', FALSE),
(6, 1, 16, '2025-02-28', FALSE),
(7, 1, 27, '2025-02-28', FALSE),
(8, 1, 26, '2025-02-28', FALSE),
(9, 1, 21, '2025-02-28', FALSE),
(10, 1, 17, '2025-02-28', FALSE),
(11, 1, 11, '2025-02-28', FALSE),
(12, 1, 13, '2025-02-28', FALSE),
(13, 1, 14, '2025-02-28', FALSE),
(14, 1, 34, '2025-01-22', TRUE),
(15, 1, 37, '2025-01-22', FALSE),
(16, 1, 31, '2025-01-22', FALSE),
(17, 1, 41, '2024-05-14', FALSE),
-- Emilia Pérez (film_id = 2)
(18, 2, 40, '2024-05-25', TRUE),
(19, 2, 39, '2024-05-25', TRUE),
(20, 2, 30, '2025-01-22', TRUE),
(21, 2, 32, '2025-01-22', FALSE),
(22, 2, 33, '2025-01-22', FALSE),
(23, 2, 29, '2025-01-22', FALSE),
(24, 2, 18, '2025-02-23', FALSE),
(25, 2, 28, '2025-02-23', TRUE),
(26, 2, 12, '2025-02-23', FALSE),
(27, 2, 15, '2025-02-23', FALSE),
(28, 2, 14, '2025-02-23', FALSE),
(29, 2, 18, '2025-02-23', FALSE),
-- Saint Omer (film_id = 3)
(30, 3, 22, '2023-02-24', TRUE),
(31, 3, 24, '2023-02-24', TRUE),
(32, 3, 30, '2023-01-16', TRUE),
(33, 3, 32, '2023-01-16', TRUE),
(34, 3, 36, '2023-01-16', TRUE),
(35, 3, 53, '2023-03-12', FALSE),
(36, 3, 66, '2023-01-10', FALSE),
-- L'Événement (film_id = 4)
(37, 4, 73, '2021-09-11', TRUE),
(38, 4, 22, '2022-02-25', TRUE),
(39, 4, 24, '2022-02-25', TRUE),
(40, 4, 23, '2022-02-25', TRUE),
(41, 4, 27, '2022-02-25', FALSE),
(42, 4, 14, '2022-02-25', FALSE),
(43, 4, 53, '2022-03-27', FALSE),
-- Titane (film_id = 5)
(44, 5, 40, '2021-07-17', TRUE),
(45, 5, 15, '2022-02-25', TRUE),
(46, 5, 14, '2022-02-25', TRUE),
(47, 5, 13, '2022-02-25', FALSE),
(48, 5, 16, '2022-02-25', FALSE),
(49, 5, 28, '2022-02-25', FALSE),
(50, 5, 12, '2022-02-25', FALSE),
(51, 5, 17, '2022-02-25', FALSE),
(52, 5, 19, '2022-02-25', FALSE),
(53, 5, 20, '2022-02-25', FALSE),
(54, 5, 21, '2022-02-25', FALSE),
(55, 5, 30, '2022-01-17', TRUE),
(56, 5, 32, '2022-01-17', TRUE),
(57, 5, 29, '2022-01-17', FALSE),
(58, 5, 46, '2022-03-27', FALSE),
(59, 5, 59, '2022-03-13', FALSE);

-- Trailers
INSERT INTO ric_trailers (
id, url, film_id
) VALUES
-- Le Comte de Monte-Cristo
(1, 'https://fr.vid.web.acsta.net/nmedia/33/24/05/07/11/05/20602412_m_013.mp4', 1),
-- Emilia Pérez
(2, 'https://fr.vid.web.acsta.net/nmedia/33/24/06/18/11/02/20604595_m_013.mp4', 2),
-- Saint Omer
(3, 'https://fr.vid.web.acsta.net/nmedia/33/22/10/17/18/19598522_m_013.mp4', 3),
-- L'Événement
(4, 'https://fr.vid.web.acsta.net/nmedia/33/21/10/29/11/19594291_m_013.mp4', 4),
-- Titane
(5, 'https://fr.vid.web.acsta.net/nmedia/33/21/06/21/13/19590063_m_013.mp4', 5);

-- Posters
INSERT INTO ric_posters (
id, image_base64, film_id
) VALUES
-- Le Comte de Monte-Cristo
(1, 'https://fr.web.img6.acsta.net/img/29/eb/29eb8341475fdb0b19b1d7b995b70e17.jpg', 1),
-- Emilia Pérez
(2, 'https://fr.web.img2.acsta.net/img/bf/98/bf982c02ee39e172a259a3face755554.jpg', 2),
-- Saint Omer
(3, 'https://fr.web.img2.acsta.net/pictures/22/10/14/12/46/2217401.jpg', 3),
-- L'Événement
(4, 'https://fr.web.img4.acsta.net/pictures/21/11/03/08/44/2142153.jpg', 4),
-- Titane
(5, 'https://fr.web.img3.acsta.net/pictures/21/07/28/16/27/4449800.jpg', 5);


-- Credit holders
-- TODO: add missing credit holders
INSERT INTO ric_credit_holders (id, first_name, last_name, gender, type)
VALUES 
    (1, 'Alice', 'Lemoine', 'female', 'Individual'),
    (2, 'Jean', 'Durand', 'male', 'Individual'),
    (3, 'Sophie', 'Moreau', 'female', 'Individual'),
    (4, 'Paul', 'Bernard', 'male', 'Individual'),
    (5, 'Luc', 'Martin', 'male', 'Individual');

-- Roles
-- TODO: add missing roles
INSERT INTO ric_roles (id, name, is_key_role)
VALUES
    (1, 'actor', TRUE),
    (2, 'director', TRUE),
    (3, 'screenwriter', TRUE),
    (4, 'producer', TRUE);

-- Film credits
INSERT INTO ric_film_credits (id, film_id, credit_holder_id, role_id)
VALUES
    (1, 1, 1, 1),  -- Alice Lemoine - actor
    (2, 1, 2, 1),  -- Jean Durand - actor
    (3, 1, 3, 2),  -- Sophie Moreau - director
    (4, 1, 4, 3),  -- Paul Bernard - screenwriter
    (5, 1, 5, 4),  -- Luc Martin - producer
    (6, 2, 5, 4),  -- Luc Martin - producer
    (7, 2, 1, 1);  -- Alice Lemoine - actor