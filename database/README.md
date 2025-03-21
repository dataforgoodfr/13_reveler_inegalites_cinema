# Data For Good #13 - Révéler les Inégalités dans le Cinéma (RIC) - base de données


## Comment lancer et accéder à la base de données ?

Pour lancer la base de données avec le backend:
* Builder et lancer les containers: `docker-compose up --build -d`
* Vérifier qu'au moins le conteneur `db` est bien démarré : `docker compose ps`
* Accéder au container avec `psql`: `docker-compose exec db psql -U postgres`

## Commandes psql utiles
* `\l` : lister les bases de données
* `\c ric_db` : se connecter à une base de données
* `\dt` : lister les tables de la base de donnée en cours
* `\q` : quitter psql et le container


## Comment configurer la base de données ?

### Configuration depuis le backend
* Lancer le projet: `docker-compose up --build -d`
* Se connecter au backend: `docker-compose exec backend bash`
* Lancer les migrations via Alembic: `poetry run alembic -c database/alembic.ini upgrade head`
* Vérifier que le schéma est à jour: `poetry run alembic -c database/alembic.ini revision --autogenerate -m "Add missing elements"`


### Configuration manuelle avec des scripts - option dépréciée
La base de données est automatiquement initialisée au premier démarrage avec les scripts SQL suivants :

1. `0_init_database.sql` : Crée le schéma et les tables de la base de données
2. `1_insert_festivals.sql` : Insère les données des festivals de cinéma
3. `2_insert_realisateurs.sql` : Insère les données des réalisateurs

Ces scripts sont exécutés automatiquement dans l'ordre alphabétique lors du premier démarrage du conteneur PostgreSQL. Cette exécution est gérée par Docker, qui lance tous les scripts `.sql` présents dans le dossier `/docker-entrypoint-initdb.d/` du conteneur.

## Comment expérimenter avec Jupyter ?

* Lancer le projet: `docker-compose up --build -d`
* Se connecter au backend: `docker-compose exec backend bash`
* Lancer jupyter: `poetry run jupyter notebook --ip 0.0.0.0 --port 8888 --allow-root --NotebookApp.token='' --NotebookApp.password=''`
* Se rendre sur l'url suivant: `http://localhost:8888/tree/database/notebooks`
* Créer ou modifier des fichiers notebook


## Informations de Connexion
- Host : localhost
- Port : 5432
- Base de données : ric_db
- Utilisateur : postgres
- Mot de passe : postgres


## Utilisation de DBeaver (Interface Graphique)

1. Installer DBeaver :
```bash
# Pour Ubuntu/Debian
sudo apt-get update
sudo apt-get install dbeaver-ce
```

2. Configurer la connexion dans DBeaver :
   - Cliquer sur "Nouvelle Connexion"
   - Sélectionner "PostgreSQL"
   - Remplir les champs avec les informations suivantes :
     * Serveur : localhost
     * Port : 5432
     * Base de données : ric_db
     * Nom d'utilisateur : postgres
     * Mot de passe : postgres
   - Tester la connexion avec le bouton "Tester la connexion"
   - Valider pour sauvegarder

3. Fonctionnalités utiles de DBeaver :
   - Explorateur de tables
   - Éditeur SQL
   - Visualisation des données
   - Export/Import de données

## Exploration avec Jupyter Notebook

Une alternative à DBeaver est d'utiliser le notebook Jupyter fourni (`exploration.ipynb`).

1. Lancer Jupyter Notebook :
```bash
jupyter notebook
```

2. Ouvrir le fichier `exploration.ipynb` et exécuter les cellules pour explorer la base de données.

## Structure de la Base de Données

Le schéma `inegalites_cinema` contient les tables suivantes :

### Table `film`
- Stocke les informations sur les films
- Contient des détails comme le titre, la date de sortie, le pays, etc.

### Table `realisateur`
- Contient les informations sur les réalisateurs
- Inclut des données biographiques et démographiques

### Table `festival`
- Répertorie les festivals de cinéma
- Stocke les informations de localisation et historiques

## Arrêt et Redémarrage de PostgreSQL

### Arrêt Sécurisé
Pour arrêter PostgreSQL tout en conservant les données :
```bash
# Arrêter le conteneur sans supprimer les volumes
docker compose stop
```

### Redémarrage
Pour redémarrer le service après un arrêt :
```bash
docker compose start
```

### Vérification du Statut
Pour vérifier l'état du conteneur :
```bash
docker compose ps
```

Ces commandes préservent les données car :
- `stop` arrête proprement le conteneur sans supprimer les volumes
- Les données sont persistées dans le volume `./database/data`
- `start` redémarre le conteneur en utilisant les volumes existants

## En Cas de Problème

Pour réinitialiser complètement la base de données :
```bash
docker compose down -v
docker compose up -d
```

## Contact

Pour tout autre problème, vous pouvez me contacter à : joelteixeira26@gmail.com
