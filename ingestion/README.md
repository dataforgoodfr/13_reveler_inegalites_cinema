# Ingestion

## Metadata du document

**Responsable:** Joel Teixeira

**Dernière révision:** 2026-05-26

**Statut:** actif

### Historique du document

| #   | Date       | Auteur        | Observations           |
| --- | ---------- | ------------- | ---------------------- |
| 1   | 2026-05-07 | Joel Teixeira | Initial implementation |
| 2   | 2026-05-21 | Joel Teixeira | Ajout du deployment Prefect dédié au scraping Allociné. Planification automatique du scraping Allociné toutes les 10 minutes |
| 3   | 2026-05-22 | Joel Teixeira | Alignement version Prefect server/worker et ajout du troubleshooting de migration Prefect. Ajout de l'authentification basic sur l'UI et l'API Prefect. Le CLI de scraping Allociné charge automatiquement `ingestion/.env` avant de résoudre les placeholders JSON |
| 4   | 2026-05-26 | Joel Teixeira | Ajout du polling de file `ops.ingestion_run_requests` directement dans Prefect, du monitoring `ops.v_allocine_pipeline_status` et du wiring Docker Compose associé |

Ce dossier regroupe les assets d'ingestion et de transformation de données, séparés du code applicatif principal.

Ce README sert de point d'entrée rapide: statut courant, structure et commandes usuelles. Pour le setup complet, les contrats cible ou la roadmap, voir les liens en fin de document.

## Etat actuel

Strategie retenue:

1. `Airbyte` synchronise uniquement les Google Sheets source vers `raw`.
2. Pour `Modification data`, chaque onglet métier correspond à sa propre source Airbyte, sa propre connexion/sync et sa propre table brute cible.
3. `dbt` transforme les tables brutes et les sorties de scraping, puis publie les tables finales prévues par `schema1`.
4. `scraping/allocine/` exécute le scraping Allociné et écrit les données enrichies dans `raw.allocine_data`.
5. `Prefect` orchestre les syncs Airbyte via API, puis les étapes `dbt` et `scraping allocine`.
6. `Prefect` poll aussi la file `ops.ingestion_run_requests` dans la base projet, claim une requête à la fois et déclenche le deployment Prefect principal.

Pour les configs locales de debug, le CLI de scraping charge automatiquement `ingestion/.env` avant de résoudre les placeholders JSON de type `${...}`.

Ce que cela implique:

1. le scraper Allociné n'est pas exécuté par Airbyte;
2. `Airbyte` reste cantonné aux sources standards, en particulier Google Sheets;
3. le Google Sheet `Modification data` n'est pas un flux unique: il faut un sync Airbyte distinct par onglet / table métier;
4. `dbt` ne scrape rien: il transforme seulement les tables d'entrée;
5. `Prefect` devient le point d'entrée opérationnel du flux complet, y compris pour déclencher les syncs Airbyte via API.
6. le runtime Prefect expose un flow principal unique, un flow de scraping seul et un poller de demandes Metabase;
7. côté exécution réelle, `dbt phase 1` et `scraping Allociné` sont finalisés;
8. `airbyte sync` est maintenant exécutable dans Prefect à partir de noms de connexions explicites;
9. `dbt phase 2` est modélisé et exécutable lorsqu'il est explicitement activé.

Modèles implémentés:

1. `stg_films`: normalisation et typage de `raw.films`.
2. `stg_allocine_data`: normalisation de `raw.allocine_data`.
3. `int_films_latest_by_visa`: derniere ligne Films par `cnc_visa`.
4. `int_allocine_data_latest_by_source_record`: dernière version Allociné par enregistrement source.

Découpage d'exécution:

1. les modèles taggés `phase1` s'exécutent avant scraping;
2. les modèles taggés `phase2` s'exécutent après scraping;
3. `raw.allocine_data` ne doit donc pas être testé ni relu pendant `dbt phase 1`.

Point important:

1. l'entrée canonique actuelle du scraping est `raw.id_matching`;
2. la sortie canonique du scraping Allociné est `raw.allocine_data`;
3. les tables finales `fnl_*` de `schema1` restent encore largement à construire.
4. stratégie comptes recommandée: `prefect_user` pour Prefect, `airbyte_user` pour Airbyte, `dbt_user` pour le runtime `dbt + scraping` du repo.
5. dans l'état actuel du repo, le profil `dbt` utilise `dbt_user` en dur.

## Roles

1. `airbyte/`: assets, manifests versionnés et bootstrap API pour les syncs Google Sheets vers `raw`.
2. `dbt/`: transformations SQL, staging, intermediate et futures tables finales `fnl_*` dans `fnl`.
3. `scraping/allocine/`: job standalone de scraping/enrichissement Allociné.
4. `prefect/`: orchestration du pipeline d'ingestion.
5. `ops/`: schéma PostgreSQL dédié au monitoring Allociné et à la file de déclenchement ingestion.

## Bootstrap Airbyte

Le dossier [airbyte/README.md](/root/explore/13_reveler_inegalites_cinema/ingestion/airbyte/README.md:1) documente maintenant un mode de bootstrap versionné pour les sources Airbyte.

Principe retenu:

1. les manifests source sont versionnés dans `airbyte/sources/`;
2. les secrets restent hors git dans `airbyte/json_credentials/`;
3. l'utilisateur dépose un unique fichier JSON de compte de service dans `airbyte/json_credentials/`;
4. l'utilisateur renseigne lui-même l'URL du Google Sheet dans le parametre `configuration.spreadsheet_id` pour chaque source;
5. `airbyte/bootstrap.py` lit obligatoirement `AIRBYTE_CLIENT_ID` et `AIRBYTE_CLIENT_SECRET` depuis l'environnement;
6. `airbyte/bootstrap.py` infère automatiquement le workspace Airbyte s'il n'y en a qu'un;
7. `airbyte/bootstrap.py` crée ou met à jour la source Google Sheets;
8. `airbyte/bootstrap.py` crée ou met à jour la destination Postgres cible;
9. `airbyte/bootstrap.py` crée ou met à jour la connexion source -> destination correspondante.
10. les manifests `src_gsheet_*` alignés sur l'architecture cible sont déjà présents, mais leurs `spreadsheet_id` restent volontairement vides tant que les URLs réelles ne sont pas renseignées.

Variables d'environnement Airbyte désormais attendues dans `.env`:

1. `AIRBYTE_HOST` et `AIRBYTE_PORT`, ou `AIRBYTE_API_URL`
2. `POSTGRES_HOST`
3. `POSTGRES_PORT`
4. `POSTGRES_DB`
5. `AIRBYTE_DESTINATION_POSTGRES_PASSWORD`
6. `AIRBYTE_CLIENT_ID`
7. `AIRBYTE_CLIENT_SECRET`
8. `AIRBYTE_SYNC_TIMEOUT_SECONDS`
9. `AIRBYTE_SYNC_POLL_SECONDS`

Variables d'environnement Prefect désormais attendues dans `.env`:

1. `PREFECT_VERSION`
2. `PREFECT_API_DATABASE_CONNECTION_URL`
3. `PREFECT_PORT`
4. `PREFECT_AUTH_STRING`

Variables d'environnement du poller de demandes ingestion désormais attendues dans `.env`:

1. `INGESTION_REQUEST_POSTGRES_USER` ou, par défaut, `prefect_user`
2. `INGESTION_REQUEST_POSTGRES_PASSWORD`
3. `INGESTION_REQUEST_MAIN_DEPLOYMENT_NAME`
4. `INGESTION_REQUEST_POLL_INTERVAL_SECONDS`
5. `INGESTION_REQUEST_CLAIM_TIMEOUT_SECONDS`
6. `INGESTION_REQUEST_AUTO_INIT_QUEUE_SCHEMA`
7. `INGESTION_REQUEST_RUN_AIRBYTE_SYNC_STEP`
8. `INGESTION_REQUEST_RUN_DBT_PHASE_2_STEP`
9. `INGESTION_REQUEST_AIRBYTE_CONNECTION_NAMES`


Commandes utiles depuis `ingestion/`:

```bash
python3 -m ingestion.airbyte.bootstrap list-workspaces
python3 -m ingestion.airbyte.bootstrap list-sources
python3 -m ingestion.airbyte.bootstrap apply --dry-run
python3 -m ingestion.airbyte.bootstrap apply
```

## Scraping Allocine

Le job `scraping/allocine/`:

1. lit `raw.id_matching`;
2. relit `raw.allocine_data` pour éviter de retraiter ce qui est déjà terminé;
3. scrape seulement les IDs manquants;
4. écrit les résultats enrichis dans `raw.allocine_data`;
5. est lancé directement ou via Prefect, pas via Airbyte.

## Démarrage

Depuis la racine du repository, entrer dans ce workspace avant de lancer les commandes de setup:

```bash
cd ingestion
```

## Structure

- `airbyte/`: configuration et assets liés aux syncs Google Sheets
- `dbt/`: projet dbt Core
- `scraping/`: jobs de scraping versionnés et dockerisables
- `prefect/`: flows et image d'orchestration
- `docker-compose.yml`: stack Docker locale pour `prefect-server`, `prefect-worker` et `browserless`

Dans `dbt/models/`:

1. `staging/`: normalisation des sources
2. `intermediate/`: consolidation de la dernière version par clé
3. `fnl/`: futurs datasets publiés ou artefacts finaux du projet

## Runbook

Voir le [runbook de setup infra](../docs/runbooks/ingestion-runbook-infra-setup-dbt-core-airbyte-remote-postgres.md) pour les etapes de configuration, troubleshooting.


## Usage Docker

Le module `ingestion/` est maintenant dockerisable côté repo.

Services fournis dans [docker-compose.yml](/root/explore/13_reveler_inegalites_cinema/ingestion/docker-compose.yml:1):

1. stack coeur démarrée par `docker compose up`: `prefect-server`, `prefect-worker`, `browserless`
2. `prefect-worker` embarque par défaut `dbt`, le runtime du scraping Allociné et le poller des demandes d'ingestion

Limitation de ressources locale:

1. `prefect-server`: `0.50` CPU, `512m` max, `256m` réservés;
2. `prefect-worker`: `1.50` CPU, `2g` max, `768m` réservés;
3. `browserless`: `1.00` CPU, `1g` max, `512m` réservés et `shm_size=512m`;
4. ces valeurs se surchargent dans `ingestion/.env` via `PREFECT_SERVER_*`, `PREFECT_WORKER_*` et `BROWSERLESS_*`.

Exemples depuis `ingestion/`:

```bash
docker compose up -d
```

## Usage Prefect

La stack Prefect est volontairement légère.

L'UI et l'API sont protégées par une authentification basic Prefect. Au premier accès, le navigateur demande la même chaîne définie dans `.env` pour le serveur et pour les clients.

Elle utilise:

1. `prefect-server`: API + UI Prefect locale.
2. `prefect-worker`: exécution des flows.
3. une database distante dédiée `prefect` sur le serveur PostgreSQL existant.
4. `dbt` et le scraping Allociné directement dans `prefect-worker`.
5. trois deployments Prefect utilisateur sont publiés automatiquement au démarrage du worker.
6. les services internes Prefect (scheduler/runner) sont activés pour permettre la création des runs planifiés.

Services:

1. `prefect-server`
2. `prefect-worker`
UI locale:

1. dashboard Prefect: `http://localhost:$PREFECT_PORT`
2. API Prefect: `http://localhost:$PREFECT_PORT/api`

Valeur par défaut dans `.env.example`: `PREFECT_PORT=4222`.

Important:

1. `prefect-server` et `prefect-worker` doivent utiliser la meme valeur `PREFECT_VERSION`;
2. `prefect-server` et `prefect-worker` doivent partager la meme valeur `PREFECT_AUTH_STRING`;
3. les deux services Prefect sont construits depuis la meme image locale `ric-prefect:${PREFECT_VERSION}` pour eviter les ecarts entre tag Docker publie et version Python installee;
4. si la base `prefect` a deja ete initialisee par une autre ligne de versions Prefect, le serveur peut echouer au demarrage avec `Can't locate revision identified by '...'`;
5. dans ce cas, utiliser une base Prefect dediee neuve pour ce stack, ou realigner `PREFECT_VERSION` sur la version exacte qui a cree cette base.

Mode opératoire recommandé:

1. démarrer la stack avec `docker compose up -d`;
2. ouvrir l'UI Prefect;
3. attendre la publication automatique des deployments par `prefect-worker`;
4. déclencher manuellement `lancer-ingestion-donnees` selon besoin; `lancer-scraping-allocine` s'exécute automatiquement toutes les 10 minutes.

Le point d'entrée versionné est [flows.py](/root/explore/13_reveler_inegalites_cinema/ingestion/prefect/flows.py:1). Il expose maintenant plusieurs flows utilisables directement depuis l'UI Prefect:

1. `Lancer l'ingestion complete`: chaîne `airbyte sync -> dbt phase 1 -> scraping -> dbt phase 2`.
   Description: orchestration complète du pipeline avec étapes optionnelles activables au lancement.
2. `Recuperer les donnees Allocine`: exécution du scraping Allociné seul.
   Description: lance uniquement le scraping avec le fichier de configuration fourni.
3. `Traiter les demandes d'ingestion`: polling de la file `ops.ingestion_run_requests`.
   Description: claim une demande Metabase et déclenche le deployment principal.

Dans le flow principal, les étapes sont exécutées en séquence dans le même flow run pour éviter la création de sous-flows Prefect imbriqués:

1. `Synchroniser les sources`
   Description: déclenche les synchronisations Airbyte demandées par nom de connexion, attend leur statut terminal et réutilise un job déjà en cours si nécessaire.
2. `Preparer les donnees`
   Description: exécute `dbt build --select tag:phase1` avant le scraping.
3. `Recuperer les donnees Allocine`
   Description: lance le scraping Allociné avec le fichier de configuration fourni.
4. `Finaliser les donnees`
   Description: exécute `dbt build --select tag:phase2` uniquement si cette étape est activée.

Deployments publiés automatiquement:

1. `lancer-ingestion-donnees`
   Description: point d'entrée manuel recommandé pour les utilisateurs de l'UI Prefect.
2. `lancer-scraping-allocine`
   Description: exécute uniquement le flow de scraping Allociné, sans déclencher Airbyte ni dbt, avec un schedule automatique toutes les 10 minutes et une limite de concurrence à 1.
3. `traiter-les-demandes-ingestion`
   Description: poller schedulé qui lit `ops.ingestion_run_requests`, claim une ligne `pending`, lance `lancer-ingestion-donnees`, puis laisse le flow principal écrire l'état terminal.

Important:

1. la séparation `dbt avant scraping` / `dbt après scraping` est toujours conservée dans le code;
2. `dbt phase 1` exécute `dbt build --select tag:phase1`;
3. `allocine scraping` est opérationnel;
4. `dbt phase 2` exécute `dbt build --select tag:phase2`, mais reste une étape aval désactivée par défaut;
5. `airbyte sync` exige `--run-airbyte-sync`, au moins un nom de connexion Airbyte explicite, et des valeurs `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` valides dans `.env`;
6. l'étape Airbyte attend la fin de chaque job avant de passer à `dbt phase 1`;
7. le flow principal exécute la bonne séquence et saute les étapes futures tant qu'elles ne sont pas activées.

## Usage Poller

Le polling Metabase est maintenant porté directement par des flows Prefect:

1. `Traiter les demandes d'ingestion` lit la file `ops.ingestion_run_requests` déjà initialisée;
2. `request_id` est maintenant généré automatiquement par PostgreSQL via `gen_random_uuid()`;
3. il claim au plus une ligne `pending` par run via `FOR UPDATE SKIP LOCKED` et la passe en `processing`;
4. il déclenche ensuite uniquement le deployment Prefect `lancer-ingestion-donnees`;
5. le flow d'ingestion écrit ensuite l'état terminal `success` ou `failed` dans la même table;
6. `Requeue les demandes d'ingestion stale` reste disponible en CLI/code comme maintenance explicite pour les lignes `processing` trop anciennes sans flow run associé; il n'est pas publié automatiquement comme deployment schedulé.

Important:

1. par défaut, le poller n'exécute pas de DDL sur la base projet;
2. `INGESTION_REQUEST_AUTO_INIT_QUEUE_SCHEMA=true` doit être réservé à un compte PostgreSQL ayant les droits de création/altération sur `ops`;
3. en exploitation normale avec un compte restreint, créer la table/index une fois manuellement puis laisser cette option à `false`.

Artefacts associés:

1. [flows.py](/root/explore/13_reveler_inegalites_cinema/ingestion/prefect/flows.py:1): flows d'orchestration, polling SQL et maintenance.
2. [start_worker.sh](/root/explore/13_reveler_inegalites_cinema/ingestion/prefect/start_worker.sh:1): publication automatique des deployments, dont le poller schedulé.
3. [v_allocine_pipeline_status.sql](/root/explore/13_reveler_inegalites_cinema/ingestion/dbt/models/ops/v_allocine_pipeline_status.sql:1): vue `ops` pour le dashboard Metabase.


## Résumé opératoire

1. Airbyte sync les Google Sheets vers `raw`.
2. Pour la mise à jour de données, Airbyte exécute un sync séparé par onglet métier.
3. `raw.id_matching` sert de table d'entrée canonique du scraping.
4. Prefect expose maintenant trois deployments utiles: ingestion complète, scraping Allociné seul, et poller des demandes d'ingestion.
5. Si l'option Airbyte est activée, Prefect déclenche les syncs demandés par noms de connexions et attend leur fin.
6. Dans ce flow, Prefect lance ensuite `dbt phase 1` avant scraping.
7. Prefect lance ensuite le scraping Allociné.
8. Prefect prévoit enfin `dbt phase 2`, mais cette étape reste désactivée par défaut.

## Documentation détaillée

1. [README Airbyte](airbyte/README.md): bootstrap versionné des sources Airbyte, secrets locaux hors git et commandes d'application.
1. [README dbt](dbt/README.md): modèles préparés, tags d'exécution et sources brutes consommées par le projet dbt.
1. [Runbook infra](../docs/runbooks/ingestion-runbook-infra-setup-dbt-core-airbyte-remote-postgres.md): installation et exploitation locale Airbyte/dbt/PostgreSQL.
1. [Specification Airbyte/dbt](../docs/specifications/ingestion-specification-airbyte-dbt-mises-a-jour-donnees.md): contrats cible et critères d'acceptation.
1. [Architecture ingestion](../docs/architecture/ingestion-architecture-airbyte-dbt-prefect-scraping.md): cible de référence, état actuel relatif et roadmap de convergence.

## Referenced by

- [README.md](../README.md)
