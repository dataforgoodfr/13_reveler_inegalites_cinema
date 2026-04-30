# Extraction de donnees externes

Ce dossier contient les scripts historiques de collecte web du projet.

Ils utilisent en general:

- [scraping_browser.py](scraping_browser.py): session Playwright asynchrone, connectee au Chromium distant via `PLAYWRIGHT_WS_ENDPOINT`;
- BeautifulSoup: parsing du HTML rendu par Playwright;
- CSV locaux: stockage intermediaire avant seed ou controle.


## Scrapers principaux

### Allocine

Objectif: retrouver les pages Allocine des films CNC, puis enrichir un CSV avec metadonnees, affiche, bande-annonce, casting, equipe et societes.

Documentation: [allocine/README.md](allocine/README.md)

Point d'entree actuel:

```bash
poetry run python -m database.data.allocine.allocine_runner --matcher
poetry run python -m database.data.allocine.allocine_runner --enricher
```

### MUBI

Objectif: recuperer les films listes par festival/annee sur MUBI, puis enrichir ces films avec leurs recompenses et nominations.

Documentation: [mubi/README.md](mubi/README.md)

Note: les classes MUBI sont dans le repo, mais les fichiers actuels ne declarent pas de CLI `argparse` / `__main__`.

## Autres extractions

- [cnc/extract_cnc_data_from_excel.py](cnc/extract_cnc_data_from_excel.py): extraction depuis le fichier Excel CNC; pas du scraping web.
- [../notebooks/3_insert_tmdb_data.ipynb](../notebooks/3_insert_tmdb_data.ipynb): ancien notebook d'appel API TMDB.
- [../../ml-image/scripts/utils.py](../../ml-image/scripts/utils.py): telechargement d'affiche et de trailer depuis une URL Allocine pour la pipeline image/video.

## Evolution prevue

La specification Airbyte/dbt prevoit d'encapsuler ces scripts de scraping existants dans des connecteurs Airbyte custom.

Voir [../../docs/specifications/specification-airbyte-dbt-mises-a-jour-donnees.md](../../docs/specifications/specification-airbyte-dbt-mises-a-jour-donnees.md).
