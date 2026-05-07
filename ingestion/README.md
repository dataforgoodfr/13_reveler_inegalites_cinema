**Owner:** Joel Teixeira

**Last reviewed:** 2026-05-07

**Status:** active

## Historique du document

| # | Date       | Author         | Observations           |
|---|------------|----------------|------------------------|
| 1 | 2026-05-07 | Joel Teixeira  | Initial implementation |

# Ingestion

Ce dossier regroupe les assets d'ingestion et de transformation de données, séparés du code applicatif principal.

Ce README sert de point d'entrée rapide: statut courant, structure et commandes usuelles. Pour le setup complet, les contrats cible ou la roadmap, voir les liens en fin de document.

## Etat actuel

Strategie retenue:

1. `Airbyte` synchronise uniquement les Google Sheets source vers `raw`.
2. Pour `Modification data`, chaque onglet métier correspond à sa propre source Airbyte, sa propre connexion/sync et sa propre table brute cible.
3. `dbt` transforme les tables brutes et les sorties de scraping, puis publie les tables finales prévues par `schema1`.
4. `scraping/allocine/` exécute le scraping Allociné et écrit les données enrichies dans `raw.allocine_data`.
5. `Prefect` orchestre les étapes `dbt` et `scraping allocine`; le déclenchement des syncs Airbyte via API reste modélisé mais non implémenté.

Ce que cela implique:

1. le scraper Allociné n'est pas exécuté par Airbyte;
2. `Airbyte` reste cantonné aux sources standards, en particulier Google Sheets;
3. le Google Sheet `Modification data` n'est pas un flux unique: il faut un sync Airbyte distinct par onglet / table métier;
4. `dbt` ne scrape rien: il transforme seulement les tables d'entrée;
5. `Prefect` devient le point d'entrée opérationnel pour `dbt` et le scraping; l'étape Airbyte via API reste un placeholder non opérationnel.
6. le runtime Prefect est désormais structuré autour d'un flow principal unique et de sous-flows par étape pour garder une visibilité séparée dans l'UI;
7. côté exécution réelle, `dbt phase 1` et `scraping Allociné` sont finalisés;
8. `airbyte sync` est déjà modélisé dans Prefect mais reste une étape future;
9. `dbt phase 2` est modélisé et exécutable lorsqu'il est explicitement activé.

Modèles implémentés:

1. `stg_agreement_cnc`: normalisation et typage de `raw.agreement_cnc`.
2. `stg_allocine_data`: normalisation de `raw.allocine_data`.
3. `int_agreement_cnc_latest_by_visa`: derniere ligne Agreement CNC par `visa_number`.
4. `int_allocine_data_latest_by_source_record`: dernière version Allociné par enregistrement source.

Découpage d'exécution:

1. les modèles taggés `phase1` s'exécutent avant scraping;
2. les modèles taggés `phase2` s'exécutent après scraping;
3. `raw.allocine_data` ne doit donc pas être testé ni relu pendant `dbt phase 1`.

Point important:

1. l'entrée canonique actuelle du scraping est `raw.airbyte_id_matching`;
2. la sortie canonique du scraping Allociné est `raw.allocine_data`;
3. les tables finales `fnl_*` de `schema1` restent encore largement à construire.
4. stratégie comptes recommandée: `prefect_user` pour Prefect, `airbyte_user` pour Airbyte, `dbt_user` pour le runtime `dbt + scraping` du repo.
5. dans l'état actuel du repo, le profil `dbt` utilise `dbt_user` en dur.

## Roles

1. `airbyte/`: assets, manifests versionnés et bootstrap API pour les syncs Google Sheets vers `raw`.
2. `dbt/`: transformations SQL, staging, intermediate et futures tables finales `fnl_*` dans `fnl`.
3. `scraping/allocine/`: job standalone de scraping/enrichissement Allociné.
4. `prefect/`: orchestration du pipeline d'ingestion.

## Bootstrap Airbyte

Le dossier [airbyte/README.md](/root/explore/13_reveler_inegalites_cinema/ingestion/airbyte/README.md:1) documente maintenant un mode de bootstrap versionné pour les sources Airbyte.

Principe retenu:

1. les manifests source sont versionnés dans `airbyte/sources/`;
2. les secrets restent hors git dans `airbyte/json_credentials/`;
3. l'utilisateur dépose un unique fichier JSON de compte de service dans `airbyte/json_credentials/`;
4. l'utilisateur renseigne lui-même l'URL du Google Sheet dans `configuration.spreadsheet_id` pour chaque source;
5. `airbyte/bootstrap.py` récupère automatiquement les credentials API Airbyte via `abctl local credentials` si les variables d'environnement ne sont pas déjà définies;
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

Variables Airbyte facultatives:

1. `AIRBYTE_WORKSPACE_ID`
2. `AIRBYTE_CLIENT_ID`
3. `AIRBYTE_CLIENT_SECRET`
4. `AIRBYTE_DESTINATION_NAME`
5. `AIRBYTE_CONNECTION_PREFIX`

Commandes utiles depuis `ingestion/`:

```bash
python3 airbyte/bootstrap.py list-workspaces
python3 airbyte/bootstrap.py list-sources
python3 airbyte/bootstrap.py apply --dry-run
python3 airbyte/bootstrap.py apply
```

## Scraping Allocine

Le job `scraping/allocine/`:

1. lit `raw.airbyte_id_matching`;
2. relit `raw.allocine_data` pour éviter de retraiter ce qui est déjà terminé;
3. scrape seulement les IDs manquants;
4. écrit les résultats enrichis dans `raw.allocine_data`;
5. est lancé directement ou via Prefect, pas via Airbyte.

## Demarrage

Depuis la racine du repository, entrer dans ce workspace avant de lancer les commandes de setup:

```bash
cd ingestion
```

## Structure

- `airbyte/`: configuration et assets lies aux syncs Google Sheets
- `dbt/`: projet dbt Core
- `scraping/`: jobs de scraping versionnes et dockerisables
- `prefect/`: flows et image d'orchestration
- `docker-compose.yml`: stack Docker locale pour `prefect-server`, `prefect-worker` et `browserless`

Dans `dbt/models/`:

1. `staging/`: normalisation des sources
2. `intermediate/`: consolidation de la dernière version par clé
3. `fnl/`: futurs datasets publiés ou artefacts finaux du projet

## Runbook

Voir le [runbook de setup infra](../docs/runbooks/ingestion-runbook-infra-setup-dbt-core-airbyte-remote-postgres.md) pour les etapes de configuration et le troubleshooting.

## Lancer les modèles

Depuis `ingestion/`:

```bash
docker compose exec prefect-worker dbt build --profile ric --project-dir /app/ingestion/dbt
```

Cette commande construit les modèles dbt versionnés du module dans `prefect-worker`, qui est le runtime par défaut.

## Usage Docker

Le module `ingestion/` est maintenant dockerisable côté repo.

Services fournis dans [docker-compose.yml](/root/explore/13_reveler_inegalites_cinema/ingestion/docker-compose.yml:1):

1. stack coeur démarrée par `docker compose up`: `prefect-server`, `prefect-worker`, `browserless`
2. `prefect-worker` embarque par défaut `dbt` et le runtime du scraping Allociné

Exemples depuis `ingestion/`:

```bash
docker compose up -d
docker compose logs -f prefect-server prefect-worker browserless
docker compose exec prefect-worker dbt debug --profile ric --project-dir /app/ingestion/dbt
docker compose exec prefect-worker python3 /app/ingestion/scraping/allocine/main.py spec
```

Note:

1. `Airbyte OSS` lui-même n'est pas embarqué dans ce compose.
2. le port hôte de `browserless` est piloté par `BROWSERLESS_PORT` dans `.env`;
3. par défaut, `prefect-worker` parle au service Docker interne `browserless` sur `ws://browserless:3000`; il n'est pas nécessaire de mettre `PLAYWRIGHT_WS_ENDPOINT` dans `.env` pour ce cas standard;
4. le service `browserless` est prévu pour le dev local; un endpoint externe `PLAYWRIGHT_WS_ENDPOINT` reste possible en override explicite.

## Usage Prefect

La stack Prefect est volontairement légère.

Elle utilise:

1. `prefect-server`: API + UI Prefect locale.
2. `prefect-worker`: exécution des flows.
3. une database distante dédiée `prefect` sur le serveur PostgreSQL existant.
4. `dbt` et le scraping Allociné directement dans `prefect-worker`.
5. un seul deployment Prefect utilisateur est publié automatiquement au démarrage du worker.

Services:

1. `prefect-server`
2. `prefect-worker`

Pré-requis:

1. créer une database PostgreSQL dédiée `prefect`;
2. créer un utilisateur dédié `prefect_user`;
3. renseigner `PREFECT_PORT` dans `.env` si `4200` ou `4222` ne conviennent pas;
4. renseigner `PREFECT_API_DATABASE_CONNECTION_URL` dans `.env`;
5. vérifier que `dbt_user` existe et possède les grants attendus côté base applicative.
6. renseigner `DBT_USER_POSTGRES_PASSWORD` dans `.env` pour `dbt` et le scraping Allociné.

Exemples depuis `ingestion/`:

```bash
docker compose up -d
docker compose logs -f prefect-server prefect-worker browserless
```

UI locale:

1. dashboard Prefect: `http://localhost:$PREFECT_PORT`
2. API Prefect: `http://localhost:$PREFECT_PORT/api`

Valeur par défaut dans `.env.example`: `PREFECT_PORT=4222`.

Mode opératoire recommandé:

1. démarrer la stack avec `docker compose up -d`;
2. ouvrir l'UI Prefect;
3. attendre la publication automatique des deployments par `prefect-worker`;
4. déclencher manuellement les flows depuis l'UI.

Le point d'entrée versionné est [flows.py](/root/explore/13_reveler_inegalites_cinema/ingestion/prefect/flows.py:1). Il expose maintenant un seul flow utilisateur dans Prefect:

1. `Lancer l'ingestion complete`: chaîne `airbyte sync placeholder -> dbt phase 1 -> scraping -> dbt phase 2`.
Description: orchestration complète du pipeline avec étapes optionnelles activables au lancement.

Les étapes internes restent visibles comme sous-flows distincts dans l'exécution du flow principal, avec des libellés lisibles:

1. `Synchroniser les sources`
Description: représente l'étape de synchronisation Airbyte; elle reste non implémentée tant qu'aucun déclenchement API réel n'est branché.
2. `Preparer les donnees`
Description: exécute `dbt build --select tag:phase1` avant le scraping.
3. `Recuperer les donnees Allocine`
Description: lance le scraping Allociné avec le fichier de configuration fourni.
4. `Finaliser les donnees`
Description: exécute `dbt build --select tag:phase2` uniquement si cette étape est activée.

Deployments publiés automatiquement:

1. `lancer-l-ingestion-complete`
Description: point d'entrée manuel recommandé pour les utilisateurs de l'UI Prefect.

Important:

1. la séparation `dbt avant scraping` / `dbt après scraping` est toujours conservée dans le code et reste visible sous forme de sous-flows enfants du flow principal;
2. `dbt phase 1` exécute `dbt build --select tag:phase1`;
3. `allocine scraping` est opérationnel;
4. `dbt phase 2` exécute `dbt build --select tag:phase2`, mais reste une étape aval désactivée par défaut;
5. `airbyte sync` reste explicitement non implémenté et est sauté par défaut;
6. le flow principal exécute la bonne séquence et saute les étapes futures tant qu'elles ne sont pas activées.

Exemples CLI optionnels, surtout utiles pour debug local:

```bash
docker compose exec prefect-worker dbt build --profile ric --project-dir /app/ingestion/dbt
docker compose exec prefect-worker python3 /app/ingestion/prefect/flows.py main-ingestion
```

Le parsing CLI ne conserve plus qu'un point d'entrée `main-ingestion`; les anciennes commandes `dbt-phase-1`, `allocine-scraping` ou `airbyte-sync` ne sont plus exposées comme points d'entrée CLI séparés.

## Résumé opératoire

1. Airbyte sync les Google Sheets vers `raw`.
2. Pour `Modification data`, Airbyte exécute un sync séparé par onglet métier.
3. `raw.airbyte_id_matching` sert de table d'entrée canonique du scraping.
4. Prefect expose un seul deployment utilisateur pour lancer l'ingestion complète.
5. Dans ce flow, Prefect lance `dbt phase 1` avant scraping.
6. Prefect lance ensuite le scraping Allociné.
7. Prefect prévoit enfin `dbt phase 2`, mais cette étape reste désactivée par défaut.
8. aujourd'hui, seules les étapes `dbt phase 1` et `scraping` sont exécutées réellement.

## Documentation détaillée

1. [README Airbyte](airbyte/README.md): bootstrap versionné des sources Airbyte, secrets locaux hors git et commandes d'application.
1. [README dbt](dbt/README.md): modèles préparés, tags d'exécution et sources brutes consommées par le projet dbt.
1. [Runbook infra](../docs/runbooks/ingestion-runbook-infra-setup-dbt-core-airbyte-remote-postgres.md): installation et exploitation locale Airbyte/dbt/PostgreSQL.
2. [Specification Airbyte/dbt](../docs/specifications/ingestion-specification-airbyte-dbt-mises-a-jour-donnees.md): contrats cible et critères d'acceptation.
3. [Architecture ingestion](../docs/architecture/ingestion-architecture-airbyte-dbt-prefect-scraping.md): cible de référence, état actuel relatif et roadmap de convergence.

## Referenced by

- [README.md](../README.md)
