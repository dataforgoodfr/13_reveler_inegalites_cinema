# Scraping Mubi — flux piloté par le référentiel CNC

## Metadata du document

**Responsable:** Joel Teixeira

**Dernière révision:** 2026-06-25

**Statut:** actif

### Historique du document

| #   | Date       | Auteur        | Observations                          |
| --- | ---------- | ------------- | ------------------------------------- |
| 1   | 2026-06-25 | Joel Teixeira | Flux Mubi restreint aux films du CNC  |

Job de scraping Mubi **piloté par l'entrée** (input-driven), en alternative au job de découverte `ingestion/scraping/mubi/`.

Objectif : ne scraper **que les films pour lesquels le CNC a donné son accord**, au lieu de crawler l'intégralité des festivals Mubi (plusieurs centaines de festivals × dizaines d'années × pages) puis de filtrer en aval. Le volume scrapé est ainsi borné à la liste de référence CNC.

## Différence avec le job `mubi/`

| | `mubi/` (découverte) | `mubi_cnc/` (ce job) |
| --- | --- | --- |
| Pilotage | Crawl de tous les festivals Mubi | Liste `raw.id_matching` (films CNC) |
| Point d'entrée par film | Pages de festivals | `ID_MUBI` numérique → page du film |
| Volume | Très élevé | Borné aux films CNC |
| Tables de sortie | `raw.mubi_festival_films`, `raw.mubi_film_awards` | **Identiques** |

Les deux jobs écrivent dans les **mêmes tables** avec les **mêmes colonnes** ; les modèles dbt en aval sont inchangés. La déduplication par `record_hash` empêche l'insertion de lignes dupliquées si les deux jobs traitent un même film/édition.

## Ce que fait la source

Deux phases séquentielles à chaque exécution.

**Phase A — Palmarès par film CNC**

Lit `raw.id_matching` et récupère les `ID_MUBI` non nuls (les films CNC référencés sur Mubi). Pour chaque film **non encore traité**, charge `https://mubi.com/fr/films/{ID_MUBI}/awards` (Mubi redirige l'URL par identifiant numérique vers l'URL à slug). Les récompenses sont lues depuis le tableau structuré `pageProps.awards` de la payload Next.js `__NEXT_DATA__` (plus robuste que les sélecteurs `css-*`) : chaque entrée porte `year`, `status`, `full_display_text`, et l'événement (`industry_event`) avec son `name`, son `slug` et son `type`. Écrit un enregistrement par récompense dans `raw.mubi_film_awards`, en réutilisant le même découpage `(year, distinction, award)` que le job de découverte. Collecte au passage l'ensemble des éditions `(festival_slug, year)` dont l'événement est de type `festival`.

**Phase B — Films en sélection des éditions concernées**

Scrape uniquement les éditions `(festival_slug, year)` collectées en Phase A (et non tous les festivals × toutes les années). Pour chaque édition non encore traitée, pagine `mubi.com/fr/awards-and-festivals/{slug}?page=N&year=Y` avec le même parseur HTML que le job de découverte (`extract_festival_edition_all_films`). Écrit un enregistrement par film dans `raw.mubi_festival_films`.

## Langue / locale (anglais vs français)

Le contenu localisé de Mubi (mot de distinction `Lauréat`/`Winner`, intitulé du prix, nom du festival) **dépend de la locale de l'URL**. Pour rester cohérent avec les lignes déjà écrites par le job `mubi/` dans les mêmes tables, ce job force la locale **`/fr/`** : `distinction`, `award` et `festival` sont donc en français.

En revanche, le scrape des éditions en Phase B est piloté par `industry_event.slug` (ex. `cannes`, `oscars`), qui est **invariant par langue** — jamais par le nom affiché. Le fait de figer la locale garantit aussi un `record_hash` stable entre exécutions (un même palmarès produit toujours le même hash), ce qui rend la déduplication fiable.

## Déduplication

Trois niveaux empêchent re-scraping et lignes dupliquées :

1. **Skip incrémental (Phase A)** : un film dont l'`ID_MUBI` figure déjà dans `raw.mubi_film_awards` avec un statut complété (`success`/`no_awards`) n'est pas re-scrapé. Les statuts `error`/`blocked` ne sont pas complétés et seront réessayés au prochain run.
2. **Skip incrémental (Phase B)** : une édition `(festival_slug, year, page)` déjà présente avec un statut complété (`success`/`empty`) est ignorée ; la borne « page vide » stoppe la pagination. Au sein d'un run, chaque édition n'est scrapée qu'une fois même si plusieurs films CNC y renvoient.
3. **Dédup à l'insertion** : avant insertion, tout enregistrement dont le `record_hash` (SHA-256 du contenu) existe déjà dans la table cible — ou apparaît deux fois dans le même lot — est écarté.

## Contrat de sortie

Identique au job `mubi/`. Voir `ingestion/scraping/mubi/README.md` pour le détail des colonnes de `raw.mubi_festival_films` et `raw.mubi_film_awards`. Note : `festival_name` est renseigné avec le `festival_slug` (le nom affiché localisé n'est pas requis en aval) et `page_num` reflète la pagination de l'édition.

## Configuration

Fichier de référence : `ingestion/scraping/mubi_cnc/config.json`.

Champs spécifiques à ce job :

| Champ | Description |
| --- | --- |
| `input_schema` / `input_table` | Table de référence CNC (défaut `raw.id_matching`) |
| `input_mubi_id_column` | Colonne portant l'identifiant Mubi numérique (défaut `ID_MUBI`) |
| `scrape_limit` | Borne le nombre de films CNC traités en Phase A (tests). `null` en production. |

Les autres champs (`output_schema`, tables de sortie, délais, retry, navigateur) sont identiques au job `mubi/`.

## Commandes

```bash
# Schéma de configuration
docker compose -f ingestion/docker-compose.yml exec prefect-worker \
  python3 /app/ingestion/scraping/mubi_cnc/main.py spec

# Connectivité + présence de la table d'entrée CNC
docker compose -f ingestion/docker-compose.yml exec prefect-worker \
  python3 /app/ingestion/scraping/mubi_cnc/main.py check \
  --config /app/ingestion/scraping/mubi_cnc/config.json

# Sync complet (Phase A puis Phase B)
docker compose -f ingestion/docker-compose.yml exec prefect-worker \
  python3 -u /app/ingestion/scraping/mubi_cnc/main.py sync \
  --config /app/ingestion/scraping/mubi_cnc/config.json
```

Pour un test limité, utiliser `config-debug.json` (`scrape_limit` réduit, `verbose: true`).

## Limites importantes

1. Le job ne peut atteindre que les films CNC dont `ID_MUBI` est renseigné dans `id_matching`. Les films sans `ID_MUBI` ne sont pas scrapés (par conception).
2. La résolution par identifiant numérique et l'extraction des récompenses reposent sur la structure `__NEXT_DATA__` de Next.js. Si Mubi change son frontend, ces mécanismes peuvent nécessiter une mise à jour.
3. Le rapprochement avec un film déjà scrapé par le job `mubi/` se fait sur `mubi_id`. Une ancienne ligne avec `mubi_id` nul ne sera pas reconnue comme traitée ; le film sera re-scrapé (les nouvelles lignes, porteuses du `mubi_id`, sont conservées par `stg_mubi_film_awards` qui ne garde que le dernier run par `film_link`).
4. Le scraping des éditions (Phase B) utilise toujours les sélecteurs HTML `css-*` de `mubi_scraper.py`, susceptibles d'être modifiés par Mubi.
