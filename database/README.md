# Guide de Configuration de la Base de Données sur votre Machine

## Installation de Docker Compose

1. Installer Docker Engine en suivant la documentation officielle :
```bash
# Ajout du repository Docker
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Ajout du repository Docker aux sources APT
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installation de Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

2. Vérifier l'installation :
```bash
docker compose version
```

3. (Optionnel) Configurer Docker pour s'exécuter sans sudo :
```bash
sudo usermod -aG docker $USER
newgrp docker
```

## Prérequis
- Docker et Docker Compose installés sur votre machine
- Git pour cloner le projet

## Installation et Démarrage

1. Lancer la base de données PostgreSQL :
```bash
docker compose up db -d
```

2. Vérifier que le conteneur est bien démarré :
```bash
docker compose ps
```

## Configuration de la Base de Données

La base de données est automatiquement initialisée au premier démarrage avec les scripts SQL suivants :

1. `0_init_database.sql` : Crée le schéma et les tables de la base de données
2. `1_insert_festivals.sql` : Insère les données des festivals de cinéma
3. `2_insert_realisateurs.sql` : Insère les données des réalisateurs

...

Ces scripts sont exécutés automatiquement dans l'ordre alphabétique lors du premier démarrage du conteneur PostgreSQL. Cette exécution est gérée par Docker, qui lance tous les scripts `.sql` présents dans le dossier `/docker-entrypoint-initdb.d/` du conteneur.

Pour vérifier que tout est correctement installé, connectez-vous à la base de données :
```bash
docker exec -it 13_reveler_inegalites_cinema-db-1 psql -U postgres -d ric_db
```

Puis listez les tables :
```sql
\dt inegalites_cinema.*
```

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
