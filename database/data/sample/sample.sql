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
(1, 1, 20, '2025-02-28', true),
(2, 1, 19, '2025-02-28', true),
(3, 1, 15, '2025-02-28', false),
(4, 1, 25, '2025-02-28', false),
(5, 1, 28, '2025-02-28', false),
(6, 1, 16, '2025-02-28', false),
(7, 1, 27, '2025-02-28', false),
(8, 1, 26, '2025-02-28', false),
(9, 1, 21, '2025-02-28', false),
(10, 1, 17, '2025-02-28', false),
(11, 1, 11, '2025-02-28', false),
(12, 1, 13, '2025-02-28', false),
(13, 1, 14, '2025-02-28', false),
(14, 1, 34, '2025-01-22', true),
(15, 1, 37, '2025-01-22', false),
(16, 1, 31, '2025-01-22', false),
(17, 1, 41, '2024-05-14', false),
-- Emilia Pérez (film_id = 2)
(18, 2, 40, '2024-05-25', true),
(19, 2, 39, '2024-05-25', true),
(20, 2, 30, '2025-01-22', true),
(21, 2, 32, '2025-01-22', false),
(22, 2, 33, '2025-01-22', false),
(23, 2, 29, '2025-01-22', false),
(24, 2, 18, '2025-02-23', false),
(25, 2, 28, '2025-02-23', true),
(26, 2, 12, '2025-02-23', false),
(27, 2, 15, '2025-02-23', false),
(28, 2, 14, '2025-02-23', false),
(29, 2, 18, '2025-02-23', false),
-- Saint Omer (film_id = 3)
(30, 3, 22, '2023-02-24', true),
(31, 3, 24, '2023-02-24', true),
(32, 3, 30, '2023-01-16', true),
(33, 3, 32, '2023-01-16', true),
(34, 3, 36, '2023-01-16', true),
(35, 3, 53, '2023-03-12', false),
(36, 3, 66, '2023-01-10', false),
-- L'Événement (film_id = 4)
(37, 4, 73, '2021-09-11', true),
(38, 4, 22, '2022-02-25', true),
(39, 4, 24, '2022-02-25', true),
(40, 4, 23, '2022-02-25', true),
(41, 4, 27, '2022-02-25', false),
(42, 4, 14, '2022-02-25', false),
(43, 4, 53, '2022-03-27', false),
-- Titane (film_id = 5)
(44, 5, 40, '2021-07-17', true),
(45, 5, 15, '2022-02-25', true),
(46, 5, 14, '2022-02-25', true),
(47, 5, 13, '2022-02-25', false),
(48, 5, 16, '2022-02-25', false),
(49, 5, 28, '2022-02-25', false),
(50, 5, 12, '2022-02-25', false),
(51, 5, 17, '2022-02-25', false),
(52, 5, 19, '2022-02-25', false),
(53, 5, 20, '2022-02-25', false),
(54, 5, 21, '2022-02-25', false),
(55, 5, 30, '2022-01-17', true),
(56, 5, 32, '2022-01-17', true),
(57, 5, 29, '2022-01-17', false),
(58, 5, 46, '2022-03-27', false),
(59, 5, 59, '2022-03-13', false);

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
INSERT INTO ric_credit_holders (
  id, type, first_name, last_name, legal_name, gender, birthdate
) VALUES
  -- Le comte de monte cristo (film id 1)
  -- Réalisateurs (role id 1)
  (101, 'Individual', 'Matthieu', 'Delaporte', NULL, 'male', NULL),
  (102, 'Individual', 'Alexandre', 'De La Patellière', NULL, 'male', NULL),
  -- Scénaristes (role id 2)
  (103, 'Individual', 'Alexandre', 'De La Patellière', NULL, 'male', NULL),
  (104, 'Individual', 'Matthieu', 'Delaporte', NULL, 'male', NULL),
  -- Auteur (role id 3)
  (105, 'Individual', 'Alexandre', 'Dumas', NULL, 'male', NULL),
  -- Acteurs et actrices (role id 4)
  (106, 'Individual', 'Pierre', 'Niney', NULL, 'male', NULL),
  (107, 'Individual', 'Bastien', 'Bouillon', NULL, 'male', NULL),
  (108, 'Individual', 'Anaïs', 'Demoustier', NULL, 'female', NULL),
  (109, 'Individual', 'Anamaria', 'Vartolomei', NULL, 'female', NULL),
  (110, 'Individual', 'Laurent', 'Lafitte', NULL, 'male', NULL),
  (111, 'Individual', 'Pierfrancesco', 'Favino', NULL, 'male', NULL),
  (112, 'Individual', 'Patrick', 'Mille', NULL, 'male', NULL),
  (113, 'Individual', 'Vassili', 'Schneider', NULL, 'male', NULL),
  -- Compositeur (role id 5)
  (114, 'Individual', 'Jérôme', 'Rebotier', NULL, 'male', NULL),
  -- Producteur (role id 8)
  (115, 'Individual', 'Dimitri', 'Rassam', NULL, 'male', NULL),
  -- Directeur de la photographie (role id 10)
  (116, 'Individual', 'Nicolas', 'Bolduc', NULL, 'male', NULL),
  -- 1er assistant réalisateur (role id 11)
  (117, 'Individual', 'Daniel', 'Noah Dittmann', NULL, 'male', NULL),
  -- 2ème assistant réalisateur (role id 12)
  (118, 'Individual', 'Amandine', 'Petit-Brisson', NULL, 'female', NULL),
  -- Directeur artistique (role id 14)
  (119, 'Individual', 'Patrick', 'Schmitt', NULL, 'male', NULL),
  -- Etalonneur (role id 17)
  (120, 'Individual', 'Richard', 'Deusy', NULL, 'male', NULL),
  -- Monteur dialogue (role id 32)
  (121, 'Individual', 'Laure-Anne', 'Darras', NULL, 'female', NULL),
  -- Chef monteur (role id 19)
  (122, 'Individual', 'Célia', 'Lafitedupont', NULL, 'female', NULL),
  -- Chef coiffeur (role id 20)
  (123, 'Individual', 'Lucas', 'Coulon', NULL, 'male', NULL),
  (124, 'Individual', 'Cécile', 'Gentilin', NULL, 'female', NULL),
  (125, 'Individual', 'Agathe', 'Dupuis', NULL, 'female', NULL),
  -- Chef costumier (role id 21)
  (126, 'Individual', 'Thierry', 'Delettre', NULL, 'male', NULL),
  -- Chef maquilleur (role id 22)
  (127, 'Individual', 'Stéphane', 'Robert', NULL, 'male', NULL),
  (128, 'Individual', 'Chloé', 'Van Lierde', NULL, 'female', NULL),
  -- Effets spéciaux maquillage (role id 23)
  (129, 'Individual', 'Pierre-Olivier', 'Persin', NULL, 'male', NULL),
  (130, 'Individual', 'Frédéric', 'Balmer', NULL, 'male', NULL),
  -- Coordinateur Post-Production (role id non spécifié)
  (131, 'Individual', 'Chloé', 'Bianchi', NULL, 'female', NULL),
  -- Superviseur post-production (role id 24)
  (132, 'Individual', 'Abraham', 'Goldblat', NULL, 'male', NULL),
  -- Coordinateur de production (role id 35)
  (133, 'Individual', 'Loraine', 'Roche-Tanguy', NULL, 'female', NULL),
  -- Chef décorateur (role id 25)
  (134, 'Individual', 'Stéphane', 'Taillasson', NULL, 'male', NULL),
  -- Régisseur général (role id 34)
  (135, 'Individual', 'Robin', 'Welch', NULL, 'male', NULL),
  (136, 'Individual', 'Alexandre', 'Houllier', NULL, 'male', NULL),
  -- Scripte (role id 26)
  (137, 'Individual', 'Marie', 'Gennesseaux', NULL, 'female', NULL),
  -- Ingénieur du son (role id 27)
  (138, 'Individual', 'David', 'Rit', NULL, 'male', NULL),
  -- Monteur son (role id 33)
  (139, 'Individual', 'Marion', 'Papinot', NULL, 'female', NULL),
  (140, 'Individual', 'Olivier', 'Touche', NULL, 'male', NULL),
  (141, 'Individual', 'Gwennolé', 'Le Borgne', NULL, 'male', NULL),
  -- Effets spéciaux (role id non spécifié)
  (142, 'Individual', 'Olivier', 'Nguyen', NULL, 'male', NULL),
  (143, 'Individual', 'Jean-Christophe', 'Magnaud', NULL, 'male', NULL),
  (144, 'Individual', 'Kenneth', 'Cassar', NULL, 'male', NULL),
  -- Coordinateurs effets visuels (role id 37)
  (145, 'Individual', 'Clémentine', 'Molinié', NULL, 'female', NULL),
  -- Producteur des effets visuels (role id 29)
  (146, 'Individual', 'Olivier', 'Cauwet', NULL, 'male', NULL),
  -- Attaché de presse (role id 36)
  (147, 'Individual', 'Kelly', 'Riffaud-Laneurit', NULL, 'female', NULL),
  (148, 'Individual', 'Dominique', 'Segall', NULL, 'female', NULL),
  -- Sociétés de production (role id 30)
  (149, 'Company', NULL, NULL, 'Pathé Films', NULL, NULL),
  (150, 'Company', NULL, NULL, 'M6 Films', NULL, NULL),
  (151, 'Company', NULL, NULL, 'Chapter 2', NULL, NULL),
  (152, 'Company', NULL, NULL, 'Fargo Films', NULL, NULL),
  -- Sociétés de distribution (role id 31)
  (153, 'Company', NULL, NULL, 'Pathé Films', NULL, NULL),
  (154, 'Company', NULL, NULL, 'Pathé International', NULL, NULL),

  -- Emilia Pérez (film id 2)
  -- Réalisateur (role id 1)
  (201, 'Individual', 'Jacques', 'Audiard', NULL, 'male', NULL),
  -- Scénariste (role id 2)
  (202, 'Individual', 'Jacques', 'Audiard', NULL, 'male', NULL),
  -- Auteur (role id 3)
  (203, 'Individual', 'Boris', 'Razon', NULL, 'male', NULL),
  -- Acteur (role id 4)
  (204, 'Individual', 'Zoe', 'Saldana', NULL, 'female', NULL),
  (205, 'Individual', 'Karla Sofía', 'Gascón', NULL, 'female', NULL),
  (206, 'Individual', 'Selena', 'Gomez', NULL, 'female', NULL),
  (207, 'Individual', 'Adriana', 'Paz', NULL, 'female', NULL),
  (208, 'Individual', 'Édgar', 'Ramírez', NULL, 'male', NULL),
  (209, 'Individual', 'Mark', 'Ivanir', NULL, 'male', NULL),
  (210, 'Individual', 'Eduardo', 'Aladro', NULL, 'male', NULL),
  (211, 'Individual', 'Emiliano Hasan', 'Jalil', NULL, 'male', NULL),
  -- Compositeur (role id 5)
  (212, 'Individual', 'Camille', NULL, NULL, 'female', NULL),
  (213, 'Individual', 'Clément', 'Ducol', NULL, 'male', NULL),
  (214, 'Individual', 'Maxence', 'Dussère', NULL, 'male', NULL),
  -- Producteur musical (role id 6)
  (215, 'Individual', 'Pierre-Marie', 'Dru', NULL, 'male', NULL),
  -- Superviseur musical (role id 7)
  (216, 'Individual', 'Pierre-Marie', 'Dru', NULL, 'male', NULL),
  -- Producteur (role id 8)
  (217, 'Individual', 'Jacques', 'Audiard', NULL, 'male', NULL),
  (218, 'Individual', 'Pascal', 'Caucheteux', NULL, 'male', NULL),
  (219, 'Individual', 'Anthony', 'Vaccarello', NULL, 'male', NULL),
  (220, 'Individual', 'Valérie', 'Schermann', NULL, 'female', NULL),
  -- Producteur délégué (role id 9)
  (221, 'Individual', 'Pauline', 'Lamy', NULL, 'female', NULL),
  -- Directeur de la photographie (role id 10)
  (222, 'Individual', 'Paul', 'Guilhaume', NULL, 'male', NULL),
  -- 1er assistant réalisateur (role id 11)
  (223, 'Individual', 'Mikaël', 'Gaudin', NULL, 'male', NULL),
  -- 2ème assistant réalisateur (role id 12)
  (224, 'Individual', 'Juliette', 'Picollot', NULL, 'female', NULL),
  -- Réalisateur de 2nd équipe (role id 13)
  (225, 'Individual', 'Jean-Baptiste', 'Pouilloux', NULL, 'male', NULL),
  -- Directeur artistique (role id 14)
  (226, 'Individual', 'Virginie', 'Montel', NULL, 'female', NULL),
  -- Directeur du casting (role id 15)
  (227, 'Individual', 'Christel', 'Baras', NULL, 'female', NULL),
  (228, 'Individual', 'Carla', 'Hool', NULL, 'female', NULL),
  -- Chorégraphe et Etalonneur (role id 16)
  (229, 'Individual', 'Damien', 'Jalet', NULL, 'male', NULL),
  -- Superviseur des costumes (role id 18)
  (230, 'Individual', 'Anthony', 'Vaccarello', NULL, 'male', NULL),
  -- Chef monteur (role id 19)
  (231, 'Individual', 'Juliette', 'Welfling', NULL, 'female', NULL),
  -- Chef coiffeur (role id 20)
  (232, 'Individual', 'Jane', 'Brizard', NULL, 'female', NULL),
  (233, 'Individual', 'Emmanuel', 'Janvier', NULL, 'male', NULL),
  -- Chef costumier (role id 21)
  (234, 'Individual', 'Virginie', 'Montel', NULL, 'female', NULL),
  -- Chef maquilleur (role id 22)
  (235, 'Individual', 'Julia', 'Floch Carbonel', NULL, 'female', NULL),
  -- Effets spéciaux maquillage (role id 23)
  (236, 'Individual', 'Jean-Christophe', 'Spadaccini', NULL, 'male', NULL),
  -- Superviseur post-production (role id 24)
  (237, 'Individual', 'Eugénie', 'Deplus', NULL, 'female', NULL),
  -- Chef décorateur (role id 25)
  (238, 'Individual', 'Emmanuelle', 'Duplay', NULL, 'female', NULL),
  (239, 'Individual', 'Cécile', 'Deleu', NULL, 'female', NULL),
  (240, 'Individual', 'Sandrine', 'Jarron', NULL, 'female', NULL),
  (241, 'Individual', 'Sandra', 'Castello', NULL, 'female', NULL),
  -- Scripte (role id 26)
  (242, 'Individual', 'Christelle', 'Meaux', NULL, 'female', NULL),
  -- Ingénieur du son (role id 27)
  (243, 'Individual', 'Cyril', 'Holtz', NULL, 'male', NULL),
  -- Chef Cascadeur (role id 28)
  (244, 'Individual', 'Yves', ' Girard', NULL, 'male', NULL),
  -- Producteur des effets visuels (role id 29)
  (245, 'Individual', 'Cédric', 'Fayolle', NULL, 'male', NULL),
  -- Société de production (role id 30)
  (246, 'Company', NULL, NULL, 'Page 114', NULL, NULL),
  (247, 'Company', NULL, NULL, 'Why Not Productions', NULL, NULL),
  (248, 'Company', NULL, NULL, 'Saint Laurent by Anthony Vaccarello & Martin Katz', NULL, NULL),
  (249, 'Company', NULL, NULL, 'Pimienta Films', NULL, NULL),
  (250, 'Company', NULL, NULL, 'Pathé Films', NULL, NULL),
  (251, 'Company', NULL, NULL, 'France 2 Cinéma', NULL, NULL),
  (252, 'Company', NULL, NULL, 'LPI Media', NULL, NULL),
  -- Société de distribution (role id 31)
  (253, 'Company', NULL, NULL, 'Pathé Films', NULL, NULL),
  (254, 'Company', NULL, NULL, 'The Veterans', NULL, NULL),

  -- Saint Omer (film id 3)
  -- Réalisateurs (role id 1)
  (301, 'Individual', 'Alice', 'Diop', NULL, 'female', NULL),
  -- Scénaristes (role id 2)
  (302, 'Individual', 'Alice', 'Diop', NULL, 'female', NULL),
  (303, 'Individual', 'Amrita', 'David', NULL, 'female', NULL),
  (304, 'Individual', 'Marie', 'Ndiaye', NULL, 'female', NULL),
  -- Acteurs et actrices (role id 4)
  (305, 'Individual', 'Kayije', 'Kagame', NULL, 'female', NULL),
  (306, 'Individual', 'Guslagie', 'Malanda', NULL, 'female', NULL),
  (307, 'Individual', 'Valérie', 'Dréville', NULL, 'female', NULL),
  (308, 'Individual', 'Aurélia', 'Petit', NULL, 'female', NULL),
  (309, 'Individual', 'Xavier', 'Maly', NULL, 'male', NULL),
  (310, 'Individual', 'Robert', 'Cantarella', NULL, 'male', NULL),
  (311, 'Individual', 'Salimata', 'Kamate', NULL, 'female', NULL),
  (312, 'Individual', 'Thomas', 'De Pourquery', NULL, 'male', NULL),
  -- Producteurs délégués (role id 9)
  (313, 'Individual', 'Toufik', 'Ayadi', NULL, 'male', NULL),
  (314, 'Individual', 'Christophe', 'Barral', NULL, 'male', NULL),
  -- Directeur de la photographie (role id 10)
  (315, 'Individual', 'Claire', 'Mathon', NULL, 'female', NULL),
  -- 1er assistant réalisateur (role id 11)
  (316, 'Individual', 'Barbara', 'Canale', NULL, 'female', NULL),
  -- Directeur du casting (role id 15)
  (317, 'Individual', 'Stéphane', 'Batut', NULL, 'male', NULL),
  -- Chef monteur (role id 19)
  (318, 'Individual', 'Amrita', 'David', NULL, 'female', NULL),
  -- Chef coiffeur (role id 20)
  (319, 'Individual', 'Élodie Namani Cyrille', NULL, NULL, 'female', NULL),
  (320, 'Individual', 'Marie', 'Goetgheluck', NULL, 'female', NULL),
  -- Chef costumier (role id 21)
  (321, 'Individual', 'Annie Melza Tiburce', NULL, NULL, 'female', NULL),
  -- Chef maquilleur (role id 22)
  (322, 'Individual', 'Élodie Namani Cyrille', NULL, NULL, 'female', NULL),
  (323, 'Individual', 'Marie', 'Goetgheluck', NULL, 'female', NULL),
  -- Superviseur post-production (role id 24)
  (324, 'Individual', 'Bénédicte', 'Pollet-Baronian', NULL, 'female', NULL),
  -- Directeur de production (role id 35)
  (325, 'Individual', 'Rym', 'Hachimi', NULL, 'female', NULL),
  (326, 'Individual', 'Paul', 'Sergent', NULL, 'male', NULL),
  -- Régisseur général (role id 34)
  (327, 'Individual', 'Emma', 'Lebot', NULL, 'female', NULL),
  -- Scripte (role id 26)
  (328, 'Individual', 'Mathilde', 'Profit', NULL, 'female', NULL),
  -- Chef décorateur (role id 25)
  (329, 'Individual', 'Anna', 'Le Mouël', NULL, 'female', NULL),
  -- Ingénieur du son (role id 27)
  (330, 'Individual', 'Dana', 'Farzanehpour', NULL, 'female', NULL),
  (331, 'Individual', 'Josefina', 'Rodriguez', NULL, 'female', NULL),
  (332, 'Individual', 'Lucile', 'Demarquet', NULL, 'female', NULL),
  (333, 'Individual', 'Emmanuel', 'Croset', NULL, 'male', NULL),
  -- Attaché de presse (role id 36)
  (334, 'Individual', 'Viviana', 'Andriani', NULL, 'female', NULL),
  (335, 'Individual', 'Aurélie', 'Dard', NULL, 'female', NULL),
  -- Sociétés de production (role id 30)
  (336, 'Company', NULL, NULL, 'Pictanovo Région Hauts de France', NULL, NULL),
  (337, 'Company', NULL, NULL, 'Arte France Cinéma', NULL, NULL),
  (338, 'Company', NULL, NULL, 'SRAB Films', NULL, NULL),
  (339, 'Company', NULL, NULL, 'Ciclic-Région Centre', NULL, NULL),
  -- Sociétés de distribution (role id 31)
  (340, 'Company', NULL, NULL, 'Les Films du Losange', NULL, NULL),
  (341, 'Company', NULL, NULL, 'Goodfellas', NULL, NULL),

  -- L'Evénement (film id 4)
  -- Réalisateurs (role id 1)
  (401, 'Individual', 'Audrey', 'Diwan', NULL, 'female', NULL),
  -- Scénaristes (role id 2)
  (402, 'Individual', 'Audrey', 'Diwan', NULL, 'female', NULL),
  (403, 'Individual', 'Marcia', 'Romano', NULL, 'female', NULL),
  -- Auteur (role id 3)
  (404, 'Individual', 'Annie', 'Ernaux', NULL, 'female', NULL),
  -- Acteurs et actrices (role id 4)
  (405, 'Individual', 'Anamaria', 'Vartolomei', NULL, 'female', NULL),
  (406, 'Individual', 'Kacey', 'Mottet Klein', NULL, 'male', NULL),
  (407, 'Individual', 'Luàna', 'Bajrami', NULL, 'female', NULL),
  (408, 'Individual', 'Louise', 'Orry-Diquéro', NULL, 'female', NULL),
  (409, 'Individual', 'Louise', 'Chevillotte', NULL, 'female', NULL),
  (410, 'Individual', 'Pio', 'Marmaï', NULL, 'male', NULL),
  (411, 'Individual', 'Sandrine', 'Bonnaire', NULL, 'female', NULL),
  (412, 'Individual', 'Leonor', 'Oberson', NULL, 'female', NULL),
  -- Compositeur (role id 5)
  (413, 'Individual', 'Evgueni', 'Galperine', NULL, 'male', NULL),
  (414, 'Individual', 'Sacha', 'Galperine', NULL, 'male', NULL),
  -- Producteur (role id 8)
  (415, 'Individual', 'Edouard', 'Weil', NULL, 'male', NULL),
  (416, 'Individual', 'Alice', 'Girard', NULL, 'female', NULL),
  -- Directeur de la photographie (role id 10)
  (417, 'Individual', 'Laurent', 'Tangy', NULL, 'male', NULL),
  -- 1er assistant réalisateur (role id 11)
  (418, 'Individual', 'Anaïs', 'Couette', NULL, 'female', NULL),
  -- Assistant réalisateur (role id non spécifié)
  (419, 'Individual', 'Anaïs', 'Couette', NULL, 'female', NULL),
  -- Directeur du casting (role id 15)
  (420, 'Individual', 'Elodie', 'Demey', NULL, 'female', NULL),
  -- Chef monteur (role id 19)
  (421, 'Individual', 'Géraldine', 'Mangenot', NULL, 'female', NULL),
  -- Chef électricien (role id 38)
  (422, 'Individual', 'Olivier', 'Mandrin', NULL, 'male', NULL),
  -- Chef coiffeur (role id 20)
  (423, 'Individual', 'Sarah', 'Mescoff', NULL, 'female', NULL),
  -- Chef costumier (role id 21)
  (424, 'Individual', 'Isabelle', 'Pannetier', NULL, 'female', NULL),
  -- Chef maquilleur (role id 22)
  (425, 'Individual', 'Amélie', 'Bouilly', NULL, 'female', NULL),
  -- Superviseur post-production (role id 24)
  (426, 'Individual', 'Mélanie', 'Karlin', NULL, 'female', NULL),
  -- Coordinateur de production (role id 35)
  (427, 'Individual', 'Gary', 'Spinelli', NULL, 'male', NULL),
  -- Directeur de production (role id 35)
  (428, 'Individual', 'Monica', 'Taverna', NULL, 'female', NULL),
  -- Scripte (role id 26)
  (429, 'Individual', 'Diane', 'Brasseur', NULL, 'female', NULL),
  -- Chef décorateur (role id 25)
  (430, 'Individual', 'Diéné', 'Berete', NULL, 'female', NULL),
  -- Ingénieur du son (role id 27)
  (431, 'Individual', 'Philippe', 'Welsh', NULL, 'male', NULL),
  (432, 'Individual', 'Antoine', 'Mercier', NULL, 'male', NULL),
  -- Monteur son (role id 33)
  (433, 'Individual', 'Thomas', 'Desjonqueres', NULL, 'male', NULL),
  -- Mixage (role id 39)
  (434, 'Individual', 'Marc', 'Doisne', NULL, 'male', NULL),
  -- Attaché de presse (role id 36)
  (435, 'Individual', 'Hassan', 'Guerrar', NULL, 'male', NULL),
  (436, 'Individual', 'Julie', 'Braun', NULL, 'female', NULL),
  -- Sociétés de production (role id 30)
  (437, 'Company', NULL, NULL, 'Rectangle Productions', NULL, NULL),
  (438, 'Company', NULL, NULL, 'France 3 Cinéma', NULL, NULL),
  (439, 'Company', NULL, NULL, 'SRAB Films', NULL, NULL),
  -- Sociétés de distribution (role id 31)
  (440, 'Company', NULL, NULL, 'Wild Bunch', NULL, NULL),
  (441, 'Company', NULL, NULL, 'Goodfellas', NULL, NULL),

  -- Titane (film id 5)
  -- Réalisateurs (role id 1)
  (501, 'Individual', 'Julia', 'Ducournau', NULL, 'female', NULL),
  -- Scénaristes (role id 2)
  (502, 'Individual', 'Julia', 'Ducournau', NULL, 'female', NULL),
  -- Acteurs et actrices (role id 4)
  (503, 'Individual', 'Vincent', 'Lindon', NULL, 'male', NULL),
  (504, 'Individual', 'Agathe', 'Rousselle', NULL, 'female', NULL),
  (505, 'Individual', 'Garance', 'Marillier', NULL, 'female', NULL),
  (506, 'Individual', 'Laïs', 'Salameh', NULL, 'female', NULL),
  (507, 'Individual', 'Myriem', 'Akheddiou', NULL, 'female', NULL),
  (508, 'Individual', 'Bertrand', 'Bonello', NULL, 'male', NULL),
  (509, 'Individual', 'Dominique', 'Frot', NULL, 'female', NULL),
  -- Compositeur (role id 5)
  (510, 'Individual', 'Jim', 'Williams', NULL, 'male', NULL),
  -- Producteur (role id 8)
  (511, 'Individual', 'Jean-Christophe', 'Reymond', NULL, 'male', NULL),
  -- Producteur délégué (role id 9)
  (512, 'Individual', 'Christophe', 'Hollebeke', NULL, 'male', NULL),
  -- Coproducteur (role id 41)
  (513, 'Individual', 'Olivier', 'Père', NULL, 'male', NULL),
  (514, 'Individual', 'Jean-Yves', 'Roubin', NULL, 'male', NULL),
  (515, 'Individual', 'Cassandre', 'Warnauts', NULL, 'female', NULL),
  -- Directeur de la photographie (role id 10)
  (516, 'Individual', 'Ruben', 'Impens', NULL, 'male', NULL),
  -- 1er assistant réalisateur (role id 11)
  (517, 'Individual', 'Claire', 'Corbetta', NULL, 'female', NULL),
  -- Superviseur des effets visuels (role id 40)
  (518, 'Individual', 'Martial', 'Vallanchon', NULL, 'male', NULL),
  -- Directeur du casting (role id 15)
  (519, 'Individual', 'Constance', 'Demontoy', NULL, 'female', NULL),
  (520, 'Individual', 'Christel', 'Baras', NULL, 'female', NULL),
  -- Chef monteur (role id 19)
  (521, 'Individual', 'Jean-Christophe', 'Bouzy', NULL, 'male', NULL),
  -- Chef costumier (role id 21)
  (522, 'Individual', 'Anne-Sophie', 'Gledhill', NULL, 'female', NULL),
  -- Chef maquilleur (role id 22)
  (523, 'Individual', 'Flore', 'Masson', NULL, 'female', NULL),
  -- Superviseur post-production (role id 24)
  (524, 'Individual', 'Christina', 'Crassaris', NULL, 'female', NULL),
  (525, 'Individual', 'Sidonie', 'Waserman', NULL, 'female', NULL),
  -- Directeur de production (role id 35)
  (526, 'Individual', 'Tatiana', 'Bouchain', NULL, 'female', NULL),
  -- Chef décorateur (role id 25)
  (527, 'Individual', 'Laurie', 'Colson', NULL, 'female', NULL),
  (528, 'Individual', 'Lise', 'Péault', NULL, 'female', NULL),
  -- Ingénieur du son (role id 27)
  (529, 'Individual', 'Fabrice', 'Osinski', NULL, 'male', NULL),
  (530, 'Individual', 'Séverin', 'Favriau', NULL, 'male', NULL),
  (531, 'Individual', 'Stéphane', 'Thiébaut', NULL, 'male', NULL),
  -- Attaché de presse (role id 36)
  (532, 'Individual', 'Matilde', 'Incerti', NULL, 'female', NULL),
  (533, 'Individual', 'Thomas', 'Chanu Lambert', NULL, 'male', NULL),
  -- Sociétés de production (role id 30)
  (534, 'Company', NULL, NULL, 'Frakas Productions', NULL, NULL),
  (535, 'Company', NULL, NULL, 'Voo-BE TV', NULL, NULL),
  (536, 'Company', NULL, NULL, 'Arte France Cinéma', NULL, NULL),
  (537, 'Company', NULL, NULL, 'Kazak Productions', NULL, NULL),
  -- Sociétés de distribution (role id 31)
  (538, 'Company', NULL, NULL, 'Diaphana', NULL, NULL),
  (539, 'Company', NULL, NULL, 'Goodfellas', NULL, NULL);



-- Roles
INSERT INTO ric_roles (
  id, name, allocine_name, is_key_role
) VALUES
  (1,  'director', 'Réalisateur', true),
  (2,  'screenwriter', 'Scénariste', true),
  (3,  'writer', 'Auteur', false),
  (4,  'actor', 'Acteur', false),
  (5,  'composer', 'Compositeur', true),
  (6,  'music_producer', 'Producteur musical', false),
  (7,  'music_supervisor', 'Superviseur musical', false),
  (8,  'producer', 'Producteur', false),
  (9,  'executive_producer', 'Producteur délégué', true),
  (10, 'director_of_photography', 'Directeur de la photographie', true),
  (11, 'first_assistant_director', '1er assistant réalisateur', true),
  (12, 'second_assistant_director', '2ème assistant réalisateur', false),
  (13, 'second_unit_director', 'Réalisateur de 2nd équipe', false),
  (14, 'production_designer', 'Directeur artistique', false),
  (15, 'casting_director', 'Directeur du casting', true),
  (16, 'choreographer', 'Chorégraphe', false),
  (17, 'colorist', 'Etalonneur', false),
  (18, 'costume_supervisor', 'Superviseur des costumes', false),
  (19, 'lead_editor', 'Chef monteur', true),
  (20, 'head_hair_stylist', 'Chef coiffeur', false),
  (21, 'head_costume_designer', 'Chef costumier', true),
  (22, 'head_makeup_artist', 'Chef maquilleur', false),
  (23, 'special_effects_makeup', 'Effets spéciaux maquillage', false),
  (24, 'post_production_supervisor', 'Superviseur post-production', false),
  (25, 'production_designer', 'Chef décorateur', true),
  (26, 'script_supervisor', 'Scripte', false),
  (27, 'sound_engineer', 'Ingénieur du son', true),
  (28, 'stunt_coordinator', 'Chef Cascadeur', false),
  (29, 'visual_effects_producer', 'Producteur des effets visuels', true),
  (30, 'production_company', 'Société de production', false),
  (31, 'distribution_company', 'Société de distribution', false),
  (32, 'dialogue_editor', 'Monteur dialogue', false),
  (33, 'sound_editor', 'Monteur son', false),
  (34, 'unit_production_manager', 'Régisseur général', false),
  (35, 'production_coordinator', 'Coordinateur de production', false),
  (36, 'press_officer', 'Attaché de presse', false),
  (37, 'visual_effects_coordinator', 'Coordinateur effets visuels', false),
  (38, 'gaffer', 'Chef électricien', false),
  (39, 'mixing_engineer', 'Mixage', false),
  (40, 'visual_effects_supervisor', 'Superviseur des effets visuels', false),
  (41, 'co_producer', 'Coproducteur', false);


-- Film credits
INSERT INTO ric_film_credits (
  film_id, role_id, credit_holder_id
) VALUES
  -- Réalisateur (role id 1)
  (1, 1, 101),
  (1, 1, 102),
  (2, 1, 201),
  (3, 1, 301),
  (4, 1, 401),
  (5, 1, 501),
  -- Scénariste (role id 2)
  (1, 2, 103),
  (1, 2, 104),
  (2, 2, 202),
  (3, 2, 302),
  (3, 2, 303),
  (3, 2, 304),
  (4, 2, 402),
  (4, 2, 403),
  (5, 2, 502),
  -- Auteur (role id 3)
  (1, 3, 105),
  (2, 3, 203),
  (4, 3, 404),
  -- Acteur (role id 4)
  (1, 4, 106),
  (1, 4, 107),
  (1, 4, 108),
  (1, 4, 109),
  (1, 4, 110),
  (1, 4, 111),
  (1, 4, 112),
  (1, 4, 113),
  (2, 4, 204),
  (2, 4, 205),
  (2, 4, 206),
  (2, 4, 207),
  (2, 4, 208),
  (2, 4, 209),
  (2, 4, 210),
  (2, 4, 211),
  (3, 4, 305),
  (3, 4, 306),
  (3, 4, 307),
  (3, 4, 308),
  (3, 4, 309),
  (3, 4, 310),
  (3, 4, 311),
  (3, 4, 312),
  (4, 4, 405),
  (4, 4, 406),
  (4, 4, 407),
  (4, 4, 408),
  (4, 4, 409),
  (4, 4, 410),
  (4, 4, 411),
  (4, 4, 412),
  (5, 4, 503),
  (5, 4, 504),
  (5, 4, 505),
  (5, 4, 506),
  (5, 4, 507),
  (5, 4, 508),
  (5, 4, 509),
  -- Compositeur (role id 5)
  (1, 5, 114),
  (2, 5, 212),
  (2, 5, 213),
  (2, 5, 214),
  (4, 5, 413),
  (4, 5, 414),
  (5, 5, 510),
  -- Producteur musical (role id 6)
  (2, 6, 215),
  -- Superviseur musical (role id 7)
  (2, 7, 216),
  -- Producteur (role id 8)
  (1, 8, 115),
  (2, 8, 217),
  (2, 8, 218),
  (2, 8, 219),
  (2, 8, 220),
  (4, 8, 415),
  (4, 8, 416),
  (5, 8, 511),
  -- Producteur délégué (role id 9)
  (2, 9, 221),
  (3, 9, 313),
  (3, 9, 314),
  (5, 9, 512),
  -- Coproducteur (role id 41)
  (5, 41, 513),
  (5, 41, 514),
  (5, 41, 515),
  -- Directeur de la photographie (role id 10)
  (1, 10, 116),
  (2, 10, 222),
  (3, 10, 315),
  (4, 10, 417),
  (5, 10, 516),
  -- 1er assistant réalisateur (role id 11)
  (1, 11, 117),
  (2, 11, 223),
  (3, 11, 316),
  (4, 11, 418),
  (5, 11, 517),
  -- Assistant réalisateur (role id non spécifié)
  (4, 11, 419),
  -- 2ème assistant réalisateur (role id 12)
  (1, 12, 118),
  (2, 12, 224),
  -- Réalisateur de 2nd équipe (role id 13)
  (2, 13, 225),
  -- Directeur artistique (role id 14)
  (1, 14, 119),
  (2, 14, 226),
  -- Directeur du casting (role id 15)
  (2, 15, 227),
  (2, 15, 228),
  (3, 15, 317),
  (4, 15, 420),
  (5, 15, 519),
  (5, 15, 520),
  -- Chorégraphe (role id 16)
  (2, 16, 229),
  -- Etalonneur (role id 17)
  (1, 17, 120),
  (2, 17, 229),
  -- Superviseur des costumes (role id 18)
  (2, 18, 230),
  -- Chef monteur (role id 19)
  (1, 19, 122),
  (2, 19, 231),
  (3, 19, 318),
  (4, 19, 421),
  (5, 19, 521),
  -- Chef électricien (role id 38)
  (4, 38, 422),
  -- Chef coiffeur (role id 20)
  (1, 20, 123),
  (1, 20, 124),
  (1, 20, 125),
  (2, 20, 232),
  (2, 20, 233),
  (3, 20, 319),
  (3, 20, 320),
  (4, 20, 423),
  -- Chef costumier (role id 21)
  (1, 21, 126),
  (2, 21, 234),
  (3, 21, 321),
  (4, 21, 424),
  (5, 21, 522),
  -- Chef maquilleur (role id 22)
  (1, 22, 127),
  (1, 22, 128),
  (2, 22, 235),
  (3, 22, 322),
  (3, 22, 323),
  (4, 22, 425),
  (5, 22, 523),
  -- Superviseur post-production (role id 24)
  (1, 24, 132),
  (2, 24, 237),
  (3, 24, 324),
  (4, 24, 426),
  (5, 24, 524),
  (5, 24, 525),
  -- Directeur de production (role id 35)
  (3, 35, 325),
  (3, 35, 326),
  (4, 35, 428),
  (5, 35, 526),
  -- Coordinateur de production (role id 35)
  (4, 35, 427),
  -- Régisseur général (role id 34)
  (1, 34, 135),
  (1, 34, 136),
  (3, 34, 327),
  -- Scripte (role id 26)
  (1, 26, 137),
  (2, 26, 242),
  (3, 26, 328),
  (4, 26, 429),
  -- Chef décorateur (role id 25)
  (1, 25, 134),
  (2, 25, 238),
  (2, 25, 239),
  (2, 25, 240),
  (2, 25, 241),
  (3, 25, 329),
  (4, 25, 430),
  (5, 25, 527),
  (5, 25, 528),
  -- Ingénieur du son (role id 27)
  (1, 27, 138),
  (2, 27, 243),
  (3, 27, 330),
  (3, 27, 331),
  (3, 27, 332),
  (3, 27, 333),
  (4, 27, 431),
  (4, 27, 432),
  (5, 27, 529),
  (5, 27, 530),
  (5, 27, 531),
  -- Monteur son (role id 33)
  (1, 33, 139),
  (1, 33, 140),
  (1, 33, 141),
  (4, 33, 433),
  -- Mixage (role id 39)
  (4, 39, 434),
  -- Superviseur des effets visuels (role id 40)
  (5, 40, 518),
  -- Attaché de presse (role id 36)
  (1, 36, 147),
  (1, 36, 148),
  (3, 36, 334),
  (3, 36, 335),
  (4, 36, 435),
  (4, 36, 436),
  (5, 36, 532),
  (5, 36, 533),
  -- Sociétés de production (role id 30)
  (1, 30, 149),
  (1, 30, 150),
  (1, 30, 151),
  (1, 30, 152),
  (2, 30, 246),
  (2, 30, 247),
  (2, 30, 248),
  (2, 30, 249),
  (2, 30, 250),
  (2, 30, 251),
  (2, 30, 252),
  (3, 30, 336),
  (3, 30, 337),
  (3, 30, 338),
  (3, 30, 339),
  (4, 30, 437),
  (4, 30, 438),
  (4, 30, 439),
  (5, 30, 534),
  (5, 30, 535),
  (5, 30, 536),
  (5, 30, 537),
  -- Sociétés de distribution (role id 31)
  (1, 31, 153),
  (1, 31, 154),
  (2, 31, 253),
  (2, 31, 254),
  (3, 31, 340),
  (3, 31, 341),
  (4, 31, 440),
  (4, 31, 441),
  (5, 31, 538),
  (5, 31, 539),
  -- Monteur dialogue (role id 32)
  (1, 32, 121),
  -- Monteur son (role id 33)
  (1, 33, 139),
  (1, 33, 140),
  (1, 33, 141),
  (4, 33, 433),
  -- Régisseur général (role id 34)
  (1, 34, 135),
  (1, 34, 136),
  (3, 34, 327),
  -- Coordinateur de production (role id 35)
  (1, 35, 133),
  (4, 35, 427),
  -- Coordinateur effets visuels (role id 37)
  (1, 37, 145);


