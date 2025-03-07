# Data For Good #13 - Réduire les Inégalités dans le Cinéma (RIC) - Documentation Backend

## Requis
* `docker` et `docker-compose`

## Comment lancer le backend ?

Pour lancer le backend seul
* Builder le container: `docker build -t my-backend . -f backend/Dockerfile`
* Lancer le container: `docker run -p 5001:5001 --rm my-backend`
* Ouvrir un navigateur et se rendre à cette url: `http://localhost:5001/`

Pour lancer le backend avec la base de données
* Builder et lancer les containers: `docker-compose up --build`
* Ouvrir un navigateur et se rendre à cette url: `http://localhost:5001/`
