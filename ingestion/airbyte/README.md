# Airbyte Bootstrap

## Metadata du document

**Responsable:** Joel Teixeira

**Dernière révision:** 2026-05-08

**Statut:** actif

### Historique du document

| #   | Date       | Auteur        | Observations           |
| --- | ---------- | ------------- | ---------------------- |
| 1   | 2026-05-07 | Joel Teixeira | Initial implementation |

Ce dossier contient les manifests versionnés et les utilitaires Python pour créer, mettre à jour et piloter les ressources Airbyte via API.

## Principe

1. les manifests versionnés vivent dans `sources/`;
2. les secrets restent hors git dans `json_credentials/`;
3. l'utilisateur dépose un unique fichier JSON de compte de service dans `json_credentials/`;
4. l'utilisateur renseigne l'URL du Google Sheet cible dans `configuration.spreadsheet_id`;
5. `bootstrap.py` lit obligatoirement `AIRBYTE_CLIENT_ID` et `AIRBYTE_CLIENT_SECRET` depuis l'environnement;
6. `bootstrap.py` infère automatiquement le workspace Airbyte s'il n'y en a qu'un;
7. `bootstrap.py` injecte automatiquement le fichier JSON local dans `credentials.service_account_info`;
8. `bootstrap.py` crée ou met à jour la source Google Sheets, la destination Postgres et la connexion source -> destination;
9. `client.py` mutualise l'authentification API, la résolution du workspace, la découverte des connexions et le déclenchement des jobs de sync, réutilisés par `bootstrap.py` et `prefect/flows.py`.

## Structure

1. `bootstrap.py`: script d'application des manifests
2. `client.py`: client Airbyte partagé pour bootstrap et orchestration Prefect
3. `sources/*.json`: manifests versionnés des sources Airbyte
4. `json_credentials/`: secrets locaux gitignored

Convention recommandée:

1. un fichier manifest par source Google Sheets;
2. un `spreadsheet_id` renseigné manuellement dans chaque fichier;
3. le fichier JSON du compte de service peut avoir n'importe quel nom;
4. si le manifest n'a pas de `name`, le bootstrap utilise le nom du fichier comme nom de source Airbyte.

Manifests déjà préparés depuis l'architecture cible:

1. `src_gsheet_films.json`
2. `src_gsheet_film_id_matching.json`
3. `src_gsheet_fix_film_credits.json`
4. `src_gsheet_fix_film_genres.json`
5. `src_gsheet_fix_film_country_budget_allocation.json`
6. `src_gsheet_fix_award_nominations.json`
7. `src_gsheet_fix_credit_holders.json`
8. `src_gsheet_fix_roles.json`
9. `src_gsheet_fix_genres.json`
10. `src_gsheet_fix_countries.json`
11. `src_gsheet_fix_festivals.json`
12. `src_gsheet_fix_festival_awards.json`

## Variables d'environnement

Le script lit `ingestion/.env` par défaut et attend au minimum:

1. `AIRBYTE_HOST` et `AIRBYTE_PORT`, ou `AIRBYTE_API_URL`
2. `POSTGRES_HOST`
3. `POSTGRES_PORT`
4. `POSTGRES_DB`
5. `AIRBYTE_DESTINATION_POSTGRES_PASSWORD`
6. `AIRBYTE_CLIENT_ID`
7. `AIRBYTE_CLIENT_SECRET`


## Exemple de secret local

Créer le fichier local non commité:

```bash
mkdir -p ingestion/airbyte/json_credentials
```

Puis ajouter par exemple:

```text
ingestion/airbyte/json_credentials/ric-google-service-account.json
```

avec le JSON brut du compte de service Google.

## Commandes

Depuis `ingestion/`:

```bash
python3 -m ingestion.airbyte.bootstrap list-workspaces
python3 -m ingestion.airbyte.bootstrap list-sources
python3 -m ingestion.airbyte.bootstrap apply --dry-run
python3 -m ingestion.airbyte.bootstrap apply
```

Ou depuis la racine:

```bash
python3 -m ingestion.airbyte.bootstrap apply
```

Note:

1. l'execution supportee est `python3 -m ingestion.airbyte.bootstrap`;
2. cette forme garde des imports package propres et evite tout hack local sur `sys.path`.

## Manifest source

Exemple:

```json
{
  "kind": "source",
  "configuration": {
    "spreadsheet_id": "https://docs.google.com/spreadsheets/d/<id>/edit",
    "credentials": {
      "auth_type": "Service"
    }
  }
}
```

Le fichier versionné [sources/google-sheets.json](/root/explore/13_reveler_inegalites_cinema/ingestion/airbyte/sources/google-sheets.json:1) est un point de départ. Remplacer `REPLACE_WITH_GOOGLE_SHEET_URL` avant `apply`, ou dupliquer ce fichier pour créer plusieurs sources.

Les manifests `src_gsheet_*.json` déjà fournis dans `sources/` ont volontairement `spreadsheet_id: ""` tant que les URLs réelles ne sont pas encore connues. Ils ne sont donc pas prêts à être appliqués tant que ce champ reste vide.

Le fichier JSON du compte de service est choisi automatiquement si `json_credentials/` contient exactement un fichier JSON non ignoré.

La destination Postgres est maintenant construite automatiquement avec:

1. `POSTGRES_HOST`
2. `POSTGRES_PORT`
3. `POSTGRES_DB`
4. `AIRBYTE_DESTINATION_POSTGRES_PASSWORD`

La connexion source -> destination est aussi créée automatiquement:

1. stream(s) découverts via l'API Airbyte;
2. mode de sync pris automatiquement depuis le premier `syncMode` compatible;
3. namespace par défaut `destination`;
4. préfixe par défaut vide.

## Limites actuelles

1. la recherche d'existant se fait par `name` pour les sources et destinations;
2. les connexions sont retrouvées par paire `sourceId + destinationId`;
3. si plusieurs fichiers JSON sont présents dans `json_credentials/`, il faut expliciter le comportement avant d'automatiser davantage.
4. un manifest avec `spreadsheet_id` vide échouera volontairement au bootstrap tant que l'URL du Google Sheet n'est pas renseignée.

## Referenced by

- [ingestion/README.md](../README.md)
