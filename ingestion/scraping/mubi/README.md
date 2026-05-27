# Scraping Mubi

## Metadata du document

**Responsable:** Joel Teixeira

**Dernière révision:** 2026-05-27

**Statut:** actif

### Historique du document

| #   | Date       | Auteur        | Observations           |
| --- | ---------- | ------------- | ---------------------- |
| 1   | 2026-05-27 | Joel Teixeira | Initial implementation |

Job de scraping standalone pour la collecte des données de festivals et palmarès depuis Mubi.

Objectif : remplacer les scripts historiques dans `database/data/mubi/` par un flux brut stocké en base, orchestré par Prefect selon le même modèle que le scraping Allocine.

## Ce que fait la source

Le scraping Mubi se déroule en trois phases séquentielles à chaque exécution.

**Phase 1 — Découverte des festivals**

Pagine dynamiquement `mubi.com/fr/awards-and-festivals?type=festival&page=N` jusqu'à retourner une page vide. Produit la liste complète des festivals disponibles avec leur slug d'URL (ex. `cesars`, `cannes`). Aucune écriture en base à cette étape.

**Phase 2 — Films en sélection**

Pour chaque festival découvert, pour chaque année dans la plage `[start_year, end_year]`, et pour chaque page jusqu'à `max_pages_per_edition`, scrape les films en compétition. Chaque combinaison `(festival_slug, year, page_num)` déjà présente dans `raw.mubi_festival_films` avec un statut complété est ignorée (skip incrémental). Écrit un enregistrement par film dans `raw.mubi_festival_films`.

**Phase 3 — Palmarès par film**

Pour chaque lien de film distinct présent dans `raw.mubi_festival_films`, scrape la page de palmarès `/awards`. Extrait à la fois les récompenses et l'identifiant numérique Mubi depuis la payload Next.js `__NEXT_DATA__` embarquée dans le HTML. Les liens déjà présents dans `raw.mubi_film_awards` avec un statut complété sont ignorés. Écrit un enregistrement par récompense dans `raw.mubi_film_awards`.

## Contrat de sortie

### Table `raw.mubi_festival_films`

Un enregistrement par `(festival, année, page, film)`. Les pages sans film produisent un enregistrement sentinelle avec `scrape_status = empty` et les champs film à `null`.

| Champ | Type | Description |
| --- | --- | --- |
| `run_id` | text | Identifiant UUID du run de scraping |
| `extracted_at` | timestamptz | Horodatage d'extraction |
| `festival_slug` | text | Slug du festival (ex. `cesars`) |
| `festival_name` | text | Nom affiché du festival |
| `year` | integer | Année de l'édition |
| `page_num` | integer | Numéro de page scrapée |
| `title` | text | Titre du film sur Mubi |
| `director` | text | Réalisateur |
| `country` | text | Pays de production |
| `nominations` | text | Texte brut du nombre de nominations |
| `film_link` | text | Chemin relatif Mubi (ex. `/fr/fr/films/the-substance`) |
| `scrape_status` | text | `success`, `empty`, `blocked`, `error` |
| `error_message` | text | Message d'erreur si applicable |
| `record_hash` | text | SHA-256 du contenu pour déduplication |

### Table `raw.mubi_film_awards`

Un enregistrement par récompense individuelle. Les films sans récompense produisent un enregistrement sentinelle avec `scrape_status = no_awards`.

| Champ | Type | Description |
| --- | --- | --- |
| `run_id` | text | Identifiant UUID du run de scraping |
| `extracted_at` | timestamptz | Horodatage d'extraction |
| `film_link` | text | Chemin relatif Mubi — clé de jointure avec `mubi_festival_films` |
| `mubi_id` | integer | Identifiant numérique Mubi extrait du `__NEXT_DATA__` Next.js |
| `festival` | text | Nom du festival ayant décerné la récompense |
| `year` | text | Année de la récompense |
| `distinction` | text | Statut : `Lauréat`, `Nominé`, etc. |
| `award` | text | Intitulé précis de la récompense |
| `scrape_status` | text | `success`, `no_awards`, `blocked`, `error` |
| `error_message` | text | Message d'erreur si applicable |
| `record_hash` | text | SHA-256 du contenu pour déduplication |

## Correspondance avec la base de données

La jonction avec les films du projet se fait via `mubi_id` :

1. Le scraper extrait `mubi_id` (entier) depuis la payload `__NEXT_DATA__` de chaque page de palmarès.
2. La table `raw.id_matching` (Google Sheets) contient la colonne `ID_MUBI` pour les films déjà référencés.
3. Le modèle dbt `int_id_matching` expose ce champ sous le nom `mubi_id`.
4. Les modèles `int_mubi_festival_films` et `int_mubi_film_awards` joignent sur `mubi_id` pour résoudre `cnc_visa` et `allocine_id`.

Les films sans entrée dans `id_matching` apparaissent avec `cnc_visa = null`, ce qui permet d'identifier de nouveaux films à ajouter au référentiel.

## Configuration

Fichier de référence : `ingestion/scraping/mubi/config.json`.

```json
{
  "postgres_host": "${POSTGRES_HOST}",
  "postgres_port": "${POSTGRES_PORT}",
  "postgres_db": "${POSTGRES_DB}",
  "postgres_user": "dbt_user",
  "postgres_password": "${DBT_USER_POSTGRES_PASSWORD}",
  "postgres_sslmode": "disable",
  "output_schema": "raw",
  "festival_films_table": "mubi_festival_films",
  "film_awards_table": "mubi_film_awards",
  "start_year": 2000,
  "end_year": null,
  "max_pages_per_edition": 10,
  "festival_or_award": "festival",
  "completed_festival_statuses": ["success", "empty"],
  "completed_award_statuses": ["success", "no_awards"],
  "scrape_limit": null,
  "record_timeout_seconds": 60,
  "playwright_ws_endpoint": "${PLAYWRIGHT_WS_ENDPOINT:-ws://browserless:3000}",
  "headless": true,
  "max_requests_per_session": 6,
  "inter_request_delay_min_seconds": 2.0,
  "inter_request_delay_max_seconds": 5.0,
  "verbose": false
}
```

Les valeurs au format `${ENV_VAR:-default}` sont résolues depuis l'environnement au démarrage.

Si `database_url` est fourni, il remplace l'ensemble des champs Postgres individuels.

`scrape_limit` borne le nombre de combinaisons `(festival, année, page)` traitées lors d'un run. Utile pour les tests. Laisser à `null` en production.

`end_year` à `null` utilise l'année courante au moment de l'exécution.

## Initialisation des tables de sortie

Au premier `sync`, le job crée automatiquement les deux tables de sortie si elles n'existent pas.

Index créés au bootstrap :

Pour `mubi_festival_films` :
- `(festival_slug, year, page_num)`
- `film_link`
- `scrape_status`
- `extracted_at`

Pour `mubi_film_awards` :
- `film_link`
- `scrape_status`
- `extracted_at`

## Commandes

Depuis la racine du repo, via `docker compose exec` :

```bash
# Vérifier les imports et le schéma de configuration
docker compose -f ingestion/docker-compose.yml exec prefect-worker \
  python3 /app/ingestion/scraping/mubi/main.py spec

# Tester la connectivité à la base
docker compose -f ingestion/docker-compose.yml exec prefect-worker \
  python3 /app/ingestion/scraping/mubi/main.py check \
  --config /app/ingestion/scraping/mubi/config.json

# Lancer un sync complet (toutes les phases)
docker compose -f ingestion/docker-compose.yml exec prefect-worker \
  python3 -u /app/ingestion/scraping/mubi/main.py sync \
  --config /app/ingestion/scraping/mubi/config.json
```

Pour un test limité, ajuster temporairement `scrape_limit` dans `config.json` (ex. `2`) et passer `verbose: true` pour voir les logs détaillés par page.

Via Prefect (après redémarrage du worker ou déploiement manuel) :

```bash
docker compose -f ingestion/docker-compose.yml exec prefect-worker \
  prefect deployment run "Recuperer les donnees Mubi/lancer-scraping-mubi"
```

## Positionnement dans l'architecture

Ce job est orchestré par Prefect, pas par Airbyte. Airbyte reste réservé aux sources Google Sheets vers `raw`.

Séquence d'exécution dans le flow Prefect principal (`main_ingestion_flow`) :

```
Airbyte sync (optionnel)
  → dbt phase 1
  → scraping Allocine
  → scraping Mubi         ← ce job
  → dbt phase 2 (optionnel)
```

Le job peut aussi être déclenché de façon autonome via le déploiement `lancer-scraping-mubi`, planifié toutes les 12 minutes avec une limite de concurrence à 1.

Modèles dbt associés (tag `mubi`) :

| Modèle | Couche | Description |
| --- | --- | --- |
| `stg_mubi_festival_films` | staging | Projection typée de `raw.mubi_festival_films` |
| `stg_mubi_film_awards` | staging | Projection typée de `raw.mubi_film_awards` |
| `int_mubi_festival_films` | intermediate | Films en sélection enrichis de `cnc_visa` via `mubi_id` |
| `int_mubi_film_awards` | intermediate | Palmarès enrichis de `cnc_visa` via `mubi_id` |

## Limites importantes

1. Les sélecteurs CSS de Mubi (préfixe `css-*`) sont générés et peuvent être mis à jour par Mubi sans préavis. Le sélecteur `festival_link` utilise un pattern structurel `a[href*='/awards-and-festivals/']` pour être plus résilient, mais les autres sélecteurs dans `mubi_scraper.py` peuvent nécessiter une mise à jour manuelle.
2. L'extraction de `mubi_id` repose sur la structure `__NEXT_DATA__` de Next.js. Si Mubi change son architecture frontend, ce mécanisme peut cesser de fonctionner. Dans ce cas, `mubi_id` sera `null` et la jointure avec `id_matching` sera sans effet.
3. Le scraping est séquentiel (pas de sessions parallèles). Le volume total à traiter lors du premier run complet est élevé : plusieurs centaines de festivals × plusieurs dizaines d'années × plusieurs pages.
4. En cas de blocage anti-bot (HTTP 429), le scraper enregistre `scrape_status = blocked`, redémarre la session navigateur et continue. Les combinaisons bloquées ne sont pas marquées comme complètes et seront réessayées au prochain run.
5. Le job ne crée jamais les tables d'entrée. Il ne crée que ses propres tables de sortie.
6. Le scope de découverte est limité aux festivals (paramètre `festival_or_award = festival`). Les awards (cérémonies de type Oscar, BAFTA) peuvent être activés en changeant ce paramètre, mais les sélecteurs HTML peuvent différer.

## Scripts historiques

Les scripts d'origine se trouvent dans `database/data/mubi/` :

- `mubi_page_scraper.py` : parseur HTML de référence (repris dans ce job)
- `mubi_all_festival_films_to_csv.py` : orchestration vers CSV, remplacé par ce job
- `mubi_all_film_awards_to_csv.py` : orchestration vers CSV, remplacé par ce job
- `mubi_scraping_sandbox.ipynb` : notebook d'exploration

Ces scripts sont conservés à titre d'archive. Ce job est le point d'entrée opérationnel.
