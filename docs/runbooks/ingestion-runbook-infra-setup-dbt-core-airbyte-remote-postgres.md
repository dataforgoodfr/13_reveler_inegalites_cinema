**Owner:** Joel Teixeira

**Last reviewed:** 2026-05-07

**Status:** active

## Historique du document

| # | Date       | Author         | Observations           |
|---|------------|----------------|------------------------|
| 1 | 2026-05-07 | Joel Teixeira  | Initial implementation |

# Setup infra reproductible - Airbyte OSS + dbt Core + Prefect avec Postgres distant

## 1. Objectif

Ce runbook standardise l'installation et l'exécution de:

1. Airbyte OSS auto-hébergé
2. dbt Core
3. Prefect avec UI d'orchestration
4. environnements PostgreSQL distants (`test` et `prod` sur machines séparées)

Objectif: chaque développeur obtient le même setup, les mêmes commandes et le même comportement attendu.

Ce document est opérationnel. Il porte les commandes de setup, les variables d'environnement, les étapes de validation et le dépannage. Les contrats de données sont documentés dans la spécification; la trajectoire cible est documentée dans l'architecture ingestion.

## 2. Topologie standard

Utiliser cette topologie dans tous les environnements:

1. Airbyte OSS tourne sur la machine développeur via `abctl` pour les workflows de développement et de test.
2. Prefect tourne depuis la stack légère `ingestion/docker-compose.yml`:
   - `prefect-server` expose l'API et l'UI;
   - `prefect-worker` exécute les flows;
   - `prefect-worker` publie automatiquement les deployments versionnés au démarrage;
   - `prefect-worker` embarque le runtime `dbt Core` et le scraping Allociné;
   - l'état Prefect est stocké dans une database Postgres distante dédiée nommée `prefect`.
3. Browserless tourne dans un conteneur séparé comme dépendance runtime du scraping.
4. PostgreSQL est distant ou local:
   - machine Postgres `test`;
   - machine Postgres `prod`;
   - Postgres local optionnel pour tests isolés, mais non requis.
5. Le choix d'environnement (`test` ou `prod`) se fait côté repo via `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_SSLMODE`, `DBT_USER_POSTGRES_PASSWORD`, `PREFECT_API_DATABASE_CONNECTION_URL`, `PREFECT_PORT` et `BROWSERLESS_PORT`.
6. Le layout du repo est standardisé:
   - `ingestion/airbyte` pour les assets Airbyte;
   - `ingestion/dbt` pour les assets dbt;
   - `ingestion/prefect` pour les flows Prefect et l'image worker;
   - `ingestion/scraping` pour les jobs de scraping.

### Reproductibilité

La cohérence repose sur:

1. versions d'outils fixées;
2. contrat unique de variables d'environnement;
3. mêmes conventions de schémas et rôles entre environnements;
4. même structure de profil dbt;
5. mêmes conventions de nommage Airbyte pour sources et connexions;
6. même convention Prefect: database `prefect`, utilisateur `prefect_user`.

### Utilisateurs techniques recommandés

Utiliser des utilisateurs distincts:

1. `prefect_user`: état interne Prefect, database dédiée `prefect` uniquement;
2. `airbyte_user`: écriture de la zone brute `raw` depuis les connexions Airbyte;
3. `dbt_user`: runtime du module ingestion dans l'état actuel du repo, utilisé par `dbt` et par le scraping Allociné.

Note:

1. dans l'implémentation actuelle, `dbt` et le scraping partagent les mêmes variables de connexion runtime et le secret `DBT_USER_POSTGRES_PASSWORD`;
2. le profil `dbt` utilise `dbt_user` en dur;
3. `airbyte_user` se configure côté destination Airbyte, pas via le `docker-compose` du repo;
4. si un durcissement supplémentaire devient nécessaire plus tard, on pourra isoler un `scraping_user` dédié.

## 3. Répertoire de travail

Par défaut, partir de la racine du repo. Avant de lancer les commandes de ce runbook, entrer dans le workspace dédié:

```bash
cd ingestion
```

Sauf mention contraire, les commandes ci-dessous supposent que le répertoire courant est `ingestion/`.

## 3.1 Option Docker locale pour le module ingestion

Le repo contient aussi [ingestion/docker-compose.yml](/root/explore/13_reveler_inegalites_cinema/ingestion/docker-compose.yml:1) pour dockeriser les briques versionnées du module:

1. stack coeur démarrée par `docker compose up`: `prefect-server`, `prefect-worker`, `browserless`
2. `prefect-worker` embarque par défaut `dbt` et le runtime du scraping Allociné
3. `prefect-worker` publie un seul deployment Prefect utilisateur au démarrage

Exemples:

```bash
cd ingestion
docker compose up -d
docker compose logs -f prefect-server prefect-worker browserless
docker compose exec prefect-worker dbt debug --profile ric --project-dir /app/ingestion/dbt
docker compose exec prefect-worker python3 /app/ingestion/scraping/allocine/main.py spec
```

Cette stack ne remplace pas `Airbyte OSS` lui-même; elle dockerise le code d'ingestion versionné dans ce repo.

Stratégie opérationnelle retenue:

1. `Airbyte` sert uniquement aux Google Sheets source;
2. `Prefect` orchestre aujourd'hui `dbt` et les jobs de scraping hors Airbyte; les syncs Airbyte via API sont déjà modélisés mais restent un placeholder explicite;
3. `Prefect` stocke son état dans une database distante dédiée `prefect` sur le serveur PostgreSQL existant;
4. le scraping Allociné lit actuellement `raw.airbyte_id_matching` et écrit `raw.allocine_data`.

## 4. Prérequis

Requis sur la machine développeur:

1. Docker + Docker Compose plugin
2. `curl`
3. `python3` pour exécuter le bootstrap Airbyte versionné du repo;
4. accès distant à la database Postgres `test` et/ou `prod`;
5. accès distant à la database Prefect dédiée sur le même serveur Postgres.

Python local n'est pas requis pour `dbt`, `Prefect` et le scraping dans le chemin nominal Docker, mais reste requis pour lancer `airbyte/bootstrap.py`.
Un Postgres local peut être utilisé pour des tests isolés, mais il n'est pas requis.


## 5. Vérification préalable

Vérifier les prérequis avant installation:

```bash
docker compose version
```


## 6. Contrat de variables d'environnement

Créer un fichier local non commité nommé `.env`. Utiliser `.env.example` comme modèle:

```
cp .env.example .env
```

Puis renseigner les valeurs manquantes.


Définir `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_SSLMODE` et `DBT_USER_POSTGRES_PASSWORD` vers l'environnement cible (`test` ou `prod`) avant de lancer les commandes.
Dans l'état actuel du repo, ces variables servent au runtime `dbt + scraping` de `prefect-worker`.
Définir `PREFECT_PORT` pour choisir le port hôte local exposé par Prefect.
Définir `BROWSERLESS_PORT` pour choisir le port hôte local exposé par Browserless.
Définir `PREFECT_API_DATABASE_CONNECTION_URL` vers la database Prefect dédiée sur le même serveur Postgres cible.
Définir `AIRBYTE_HOST` et `AIRBYTE_PORT` pour l'instance Airbyte locale. L'URL UI se déduit en `http://$AIRBYTE_HOST:$AIRBYTE_PORT`.

Charger les variables dans le shell si nécessaire:

```bash
set -a
source .env
set +a
```

## 7. Préparation Postgres distant

À exécuter une fois par environnement avec un compte DBA/admin Postgres. Adapter le nom de database si besoin.

Base applicative:

```sql
CREATE USER airbyte_user WITH PASSWORD '<replace>';
CREATE USER dbt_user WITH PASSWORD '<replace>';

GRANT CONNECT ON DATABASE reveler_inegalites_cinema TO airbyte_user;
GRANT CREATE, TEMPORARY ON DATABASE reveler_inegalites_cinema TO airbyte_user;
GRANT CONNECT ON DATABASE reveler_inegalites_cinema TO dbt_user;

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS intermediate;
CREATE SCHEMA IF NOT EXISTS fnl;

ALTER SCHEMA raw OWNER TO airbyte_user;
ALTER SCHEMA staging OWNER TO dbt_user;
ALTER SCHEMA intermediate OWNER TO dbt_user;
ALTER SCHEMA fnl OWNER TO dbt_user;

GRANT USAGE, CREATE ON SCHEMA raw TO airbyte_user;
GRANT USAGE, CREATE ON SCHEMA raw TO dbt_user;

GRANT USAGE, CREATE ON SCHEMA staging TO dbt_user;
GRANT USAGE, CREATE ON SCHEMA intermediate TO dbt_user;
GRANT USAGE, CREATE ON SCHEMA fnl TO dbt_user;

-- Optionnel mais recommande pour les objets futurs crees dans raw par Airbyte
ALTER DEFAULT PRIVILEGES FOR USER airbyte_user IN SCHEMA raw
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO dbt_user;

ALTER DEFAULT PRIVILEGES FOR USER airbyte_user IN SCHEMA raw
GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO dbt_user;
```

Préparer aussi la database Prefect dédiée sur le même serveur PostgreSQL:

```sql
CREATE USER prefect_user WITH PASSWORD '<replace>';
CREATE DATABASE prefect OWNER prefect_user;

GRANT CONNECT ON DATABASE prefect TO prefect_user;
```

Dans `ingestion/.env`, renseigner ensuite:

```bash
PREFECT_API_DATABASE_CONNECTION_URL=postgresql+asyncpg://prefect_user:<replace>@<db-host>:<db-port>/prefect
```

Et pour le runtime `dbt + scraping` du repo:

```bash
DBT_USER_POSTGRES_PASSWORD=<replace>
```

Et dans Airbyte, configurer la destination Postgres avec:

```text
user = airbyte_user
password = <replace>
schema par defaut = raw
```

Si SSL est obligatoire, vérifier que le certificat racine et la chaîne de confiance sont distribués aux développeurs et configurés côté clients.

Pour `prod`, conserver les schémas canoniques (`raw`, `staging`, `intermediate`, `fnl`) et limiter les droits d'écriture à la CI/CD ou aux mainteneurs approuvés.
Pour Prefect, garder la database dédiée `prefect` séparée de la database applicative, même si les deux tournent sur le même serveur Postgres.

## 8. Setup Airbyte OSS

### Étape 1 - Installer `abctl`

Politique de version: utiliser la dernière version stable de `abctl` approuvée par l'équipe à la date d'onboarding.

```bash
curl -LsfS https://get.airbyte.com | bash
abctl version
```

### Étape 2 - Installer Airbyte en local

```bash
abctl local install --host "$AIRBYTE_HOST" --port "$AIRBYTE_PORT"
abctl local status
abctl local credentials
```

Si aucun TLS n'est configuré en local:

```bash
abctl local install --host "$AIRBYTE_HOST" --port "$AIRBYTE_PORT" --insecure-cookies
```

### Étape 3 - Accéder à l'UI

Ouvrir `http://$AIRBYTE_HOST:$AIRBYTE_PORT` et se connecter avec les identifiants retournés par `abctl local credentials`.

## 9. Configuration des connexions Airbyte

Les Google Sheets doivent exister et être partagés avec l'email du compte de service.

### Étape 0 - Configurer le compte de service GCP

1. créer un projet GCP ou utiliser un projet existant;
2. activer Google Sheets API;
3. créer un compte de service avec le rôle `Viewer`;
4. créer et télécharger une clé JSON pour ce compte de service;
5. partager les sheets avec l'email du compte de service en lecture.

### Étape 1 - Préparer les fichiers locaux

Le chemin par défaut du repo est maintenant le bootstrap versionné documenté dans [ingestion/airbyte/README.md](../../ingestion/airbyte/README.md).

Préparer:

1. un fichier JSON de clé de compte de service dans `ingestion/airbyte/json_credentials/`;
2. les manifests source dans `ingestion/airbyte/sources/`;
3. `configuration.spreadsheet_id` pour chaque source réellement activée;
4. `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_SSLMODE` et `AIRBYTE_DESTINATION_POSTGRES_PASSWORD` dans `ingestion/.env`.

Règles de fonctionnement du bootstrap:

1. le dossier `json_credentials/` est versionné mais pas son contenu;
2. le bootstrap choisit automatiquement l'unique fichier `.json` présent dans `json_credentials/`;
3. le bootstrap récupère automatiquement les credentials API Airbyte via `abctl local credentials` si besoin;
4. le bootstrap infère automatiquement le workspace Airbyte s'il n'y en a qu'un;
5. un manifest avec `spreadsheet_id` vide échoue volontairement tant que l'URL réelle du Google Sheet n'est pas renseignée.

### Étape 2 - Appliquer le bootstrap

Depuis `ingestion/`:

```bash
python3 airbyte/bootstrap.py apply --dry-run
python3 airbyte/bootstrap.py apply
```

Le bootstrap:

1. crée ou met à jour la ou les sources Google Sheets;
2. crée ou met à jour la destination Postgres;
3. crée ou met à jour la connexion source -> destination correspondante.

Convention de nommage recommandée pour `Modification data`:

1. `src_gsheet_fix_film_credits`
2. `src_gsheet_fix_film_genres`
3. `src_gsheet_fix_credit_holders`
4. `src_gsheet_fix_roles`
5. etc.

La destination Postgres générée automatiquement utilise:

1. Host: `${POSTGRES_HOST}`
2. Port: `${POSTGRES_PORT}`
3. Database: `${POSTGRES_DB}`
4. User: `airbyte_user`
5. Password: `${AIRBYTE_DESTINATION_POSTGRES_PASSWORD}`
6. schéma par défaut: `raw`
7. mode SSL: `${POSTGRES_SSLMODE}` si requis par le serveur Postgres


### Étape 3 - Validation du premier sync

Après le premier `apply`, vérifier:

1. que la source est visible dans Airbyte avec le bon `name`;
2. que la destination Postgres est visible avec `airbyte_user`;
3. que la connexion source -> destination existe;
4. que les tables brutes attendues existent dans la database Postgres configurée.

### Étape 4 - Utilisation de l'UI Airbyte en secours/debug

L'UI Airbyte n'est plus le chemin nominal de setup. Elle reste utile pour:

1. inspecter une source, une destination ou une connexion créées par le bootstrap;
2. lancer un test manuel ponctuel;
3. diagnostiquer un problème de schéma découvert, de stream ou de credential;
4. comparer l'état appliqué par API avec l'état visible côté UI.

Si un diagnostic manuel devient nécessaire, l'UI reste accessible sur `http://$AIRBYTE_HOST:$AIRBYTE_PORT`.

Après le premier sync, vérifier les tables brutes dans la database Postgres configurée:

```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema = '<your_raw_schema>'
ORDER BY table_name;
```

## 10. Setup dbt Core

Mode par défaut: `dbt Core` s'exécute dans `prefect-worker`, démarré par `docker compose up`.

### Étape 1 - Vérifier les fichiers projet dbt

```bash
test -f dbt/dbt_project.yml
```

Le scraping ne lit pas de table `fnl` de pilotage. La source de vérité actuelle du scraping est `raw.airbyte_id_matching`.

Si ce check échoue, récupérer la branche ou le contenu repo contenant le projet dbt avant de continuer.

### Étape 2 - Utiliser le profil dbt versionné

Le profil utilisé par défaut est déjà versionné dans `ingestion/dbt/profiles/profiles.yml` et disponible dans `prefect-worker`.

### Étape 3 - Valider la connectivité

```bash
test -f dbt/dbt_project.yml
docker compose exec prefect-worker dbt debug --profile ric --project-dir /app/ingestion/dbt
```

### Étape 4 - Lancer transformations et tests

```bash
docker compose exec prefect-worker dbt deps --project-dir /app/ingestion/dbt
docker compose exec prefect-worker dbt build --profile ric --project-dir /app/ingestion/dbt
```

Option de secours uniquement:

1. un venv local `dbt` reste possible si un debug hors Docker devient nécessaire;
2. ce n'est plus le chemin par défaut du module ingestion.

## 11. Setup et validation Prefect

Prefect utilise la stack Docker légère de `ingestion/docker-compose.yml`.

Services:

1. `prefect-server`: API et UI;
2. `prefect-worker`: exécution des flows;
3. `browserless`: dépendance runtime du scraping Allociné.

Démarrer la stack:

```bash
docker compose up -d
```

Valider:

```bash
docker compose logs -f prefect-server prefect-worker browserless
```

UI:

1. dashboard: `http://localhost:$PREFECT_PORT`
2. API: `http://localhost:$PREFECT_PORT/api`

Valeur par défaut dans `.env.example`: `PREFECT_PORT=4222`.

Mode opératoire recommandé:

1. démarrer la stack avec `docker compose up -d`;
2. ouvrir l'UI Prefect;
3. attendre la publication automatique des deployments par `prefect-worker`;
4. déclencher manuellement les flows depuis l'UI.

Commandes CLI optionnelles, surtout utiles pour debug local:

```bash
docker compose exec prefect-worker python3 /app/ingestion/prefect/flows.py main-ingestion
```

Convention actuelle:

1. `main-ingestion` = point d'entrée CLI unique du flow principal `airbyte sync placeholder -> dbt phase 1 -> scraping -> dbt phase 2`.
2. dans l'UI Prefect, ce flow est publié avec le libellé `Lancer l'ingestion complete`.
3. les étapes `Synchroniser les sources`, `Preparer les donnees`, `Recuperer les donnees Allocine` et `Finaliser les donnees` restent visibles comme sous-flows enfants dans le run.

Note:

1. la séparation `dbt avant scraping` / `dbt après scraping` reste volontaire, mais elle est désormais modélisée comme sous-flows enfants du flow principal;
2. `dbt phase 1` s'exécute par défaut dans `prefect-worker`;
3. `scraping Allocine` est finalisé;
4. `airbyte sync` reste présent comme étape optionnelle, mais c'est un placeholder explicite tant qu'aucune implémentation API réelle n'est branchée;
5. `dbt phase 2` existe dans le flow et peut s'exécuter si activé;
6. si `run_airbyte_sync_step=true`, le flow échoue actuellement avec `NotImplementedError`, ce qui est attendu tant que l'étape n'est pas implémentée.

## 12. Workflow développeur quotidien

Chaque développeur suit cet ordre:

1. renseigner `POSTGRES_*` dans `.env` pour l'environnement cible (`test` ou `prod`);
2. recharger les variables (`set -a; source .env; set +a`);
3. vérifier qu'Airbyte local tourne (`abctl local status`);
4. démarrer la stack ingestion si nécessaire: `docker compose up -d`;
5. déposer un unique fichier JSON de compte de service dans `ingestion/airbyte/json_credentials/`;
6. renseigner les `spreadsheet_id` nécessaires dans `ingestion/airbyte/sources/*.json`;
7. appliquer le bootstrap Airbyte: `python3 airbyte/bootstrap.py apply --dry-run && python3 airbyte/bootstrap.py apply`;
8. déclencher les syncs Airbyte depuis Airbyte UI/API ou lancer des tests manuels; ne pas considérer Prefect comme chemin opérationnel pour cette étape tant que le placeholder n'est pas implémenté;
9. vérifier au besoin dans l'UI Airbyte que la destination Postgres utilise bien `airbyte_user`;
10. lancer `docker compose exec prefect-worker dbt build --profile ric --project-dir /app/ingestion/dbt`, ou lancer le flow Prefect principal depuis l'UI;
11. lancer les runs manuellement depuis l'UI Prefect;
12. valider la couche publiée/finale consommée par backend/BI dans l'environnement cible.

## 13. Changement d'environnement

Pour changer d'environnement, modifier uniquement les valeurs de connexion:

1. modifier `.env` et pointer `POSTGRES_*` vers la database cible (`test` ou `prod`);
2. modifier `.env` et ajuster `PREFECT_PORT` si le port local choisi change;
3. modifier `.env` et ajuster `BROWSERLESS_PORT` si le port local choisi change;
4. modifier `.env` et pointer `PREFECT_API_DATABASE_CONNECTION_URL` vers la database Prefect dédiée correspondante;
5. renseigner `AIRBYTE_DESTINATION_POSTGRES_PASSWORD` pour l'environnement cible;
6. recharger les variables d'environnement (`set -a; source .env; set +a`);
7. relancer `python3 airbyte/bootstrap.py apply` pour mettre à jour la destination et les connexions avec la bonne cible;
8. garder les schémas et contrats identiques entre environnements (`raw`, `staging`, `intermediate`, `fnl`);
9. limiter les écritures production aux mainteneurs ou automatisations approuvées.

## 14. Checklist de reproductibilité

Un setup développeur est valide seulement si tous les checks passent:

1. `abctl version` correspond à la version approuvée par l'équipe;
2. `docker compose exec prefect-worker dbt --version` affiche les versions attendues du conteneur, actuellement `dbt-core 1.11.7` et `dbt-postgres 1.10.0`; cet écart est volontaire et ne doit pas être interprété comme un défaut;
3. `docker compose config --quiet` réussit;
4. l'UI Prefect est accessible sur `http://localhost:$PREFECT_PORT`;
5. Airbyte synchronise les sources Google Sheets vers `raw`;
6. `docker compose exec prefect-worker dbt debug --profile ric --project-dir /app/ingestion/dbt` réussit;
7. `docker compose exec prefect-worker dbt build --profile ric --project-dir /app/ingestion/dbt` réussit;
8. au moins un modèle est requêtable dans `staging`, `intermediate` ou `fnl`.

## 15. Problèmes fréquents

1. L'installation Airbyte échoue avec `error verifying port availability: port 8000 is already in use`:
   - vérifier la disponibilité du port candidat: `ss -ltn "( sport = :8001 )"`;
   - définir un port libre dans `.env`, par exemple `AIRBYTE_HOST=localhost` et `AIRBYTE_PORT=8001`;
   - relancer l'installation: `abctl local install --host "$AIRBYTE_HOST" --port "$AIRBYTE_PORT"`.
2. Échec de handshake SSL:
   - si l'erreur dit `server does not support SSL, but SSL was required`, définir `POSTGRES_SSLMODE=disable`;
   - si SSL est requis par le serveur, utiliser `POSTGRES_SSLMODE=require` et vérifier la chaîne de certificats.
3. Permission refusée sur schéma/table:
   - relancer les droits et privilèges par défaut de la section 7.
4. Connexion Airbyte verte mais aucune ligne:
   - vérifier le partage du spreadsheet avec l'identité du compte de service.
5. Serveur Prefect en échec de connexion database:
   - vérifier `PREFECT_API_DATABASE_CONNECTION_URL`;
   - vérifier que la database `prefect` existe et appartient à `prefect_user`;
   - vérifier l'accès réseau des conteneurs Docker vers l'hôte Postgres distant.

## 16. Références

1. démarrage rapide Airbyte OSS: https://docs.airbyte.com/platform/using-airbyte/getting-started/oss-quickstart
2. Airbyte `abctl`: https://docs.airbyte.com/platform/deploying-airbyte/abctl
3. destination Postgres Airbyte: https://docs.airbyte.com/integrations/destinations/postgres
4. installation dbt Core: https://docs.getdbt.com/docs/local/install-dbt
5. profils dbt: https://docs.getdbt.com/docs/local/profiles.yml
6. setup Postgres dbt: https://docs.getdbt.com/docs/local/connect-data-platform/postgres-setup
7. serveur Prefect auto-hébergé: https://docs.prefect.io/

## Referenced by

- [README.md](../../README.md)
- [ingestion/README.md](../../ingestion/README.md)
