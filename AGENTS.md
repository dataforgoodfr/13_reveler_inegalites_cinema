**Owner:** Data Team DataForGood

**Last reviewed:** 2026-05-07

**Status:** active

## Historique du document

| # | Date       | Author         | Observations           |
|---|------------|----------------|------------------------|
| 1 | 2026-05-07 | Joel Teixeira  | Initial implementation |

# AGENTS

## Objectif

Ce document donne les règles de travail pour intervenir dans ce repository RIC. Il sert de point d'entrée rapide pour comprendre :
- le rôle des principaux dossiers ;
- les attentes de documentation ;
- les bonnes pratiques à respecter avant de modifier le code ou les données ;
- les documents à lire en priorité selon la zone du projet.

## Périmètre Du Repository

Le repository couvre plusieurs briques liées entre elles :
- `frontend/` : application Next.js exposée aux utilisateurs finaux ;
- `backend/` : API FastAPI et logique serveur ;
- `database/` : modèles SQLAlchemy, migrations Alembic, seeds et données historiques ;
- `ingestion/` : stack Airbyte/dbt/Prefect et scraping opérationnalisé ;
- `ml-image/` : pipeline de machine learning pour l'analyse d'images et de bandes-annonces ;
- `docs/` : documentation d'architecture, spécifications, runbooks et bonnes pratiques.

## Règles De Documentation

Toute modification notable du repository doit vérifier son impact documentaire.

Règles obligatoires :
- lire [docs/repo-documentation-guidelines.md](docs/repo-documentation-guidelines.md) avant de créer ou restructurer de la documentation ;
- mettre à jour la documentation concernée dans la même PR chaque fois que possible ;
- écrire la documentation en français lorsque c'est possible, en particulier pour les contenus internes ;
- conserver en tête de chaque fichier `.md` un bloc de métadonnées avec `**Owner:**`, `**Last reviewed:**`, `**Status:**` ;
- maintenir un `## Historique du document` avec les colonnes `#`, `Date`, `Author`, `Observations` ;
- éviter les documents génériques qui mélangent plusieurs sujets.

Quand créer ou mettre à jour un document :
- nouveau workflow d'ingestion, scraping ou ML ;
- changement de comportement du backend ou du frontend ;
- évolution de schéma, migration ou seed importante ;
- nouvelle procédure d'exploitation, de debug ou de déploiement.

## Bonnes Pratiques Repository

- partir du `README.md` racine avant d'explorer un sous-dossier ;
- privilégier les `README.md` locaux pour comprendre un composant avant de modifier son code ;
- ne pas supposer que l'architecture cible est déjà implémentée ; vérifier l'état réel dans les docs d'architecture et le code ;
- pour `ingestion/`, distinguer clairement l'état actuel, la cible et les placeholders encore non finalisés ;
- pour `database/data/` et `ingestion/scraping/`, vérifier si le flux documenté est historique ou actif ;
- pour `ml-image/`, vérifier les prérequis système et les poids/modèles avant toute exécution ;
- garder les changements ciblés : un sujet technique, une doc associée, un historique mis à jour ;
- ne pas ajouter de secrets, credentials ou données sensibles dans le repo ni dans les exemples de doc.

## Workflow Recommandé

1. Identifier la zone impactée : `frontend`, `backend`, `database`, `ingestion`, `ml-image`, `docs`.
2. Lire le `README.md` local et les documents d'architecture/spécification liés.
3. Vérifier si la modification touche aussi les scripts, schémas, runbooks ou docs métier.
4. Modifier le code.
5. Mettre à jour la documentation associée et son historique.
6. Vérifier les commandes de test, build ou debug pertinentes pour la zone modifiée.

## Documentation Principale À Lire

Point d'entrée général :
- [README.md](README.md) : vision d'ensemble du projet, stack, prérequis et liens principaux.

Par composant :
- [frontend/README.md](frontend/README.md) : structure frontend, prérequis Node.js et commandes locales.
- [backend/README.md](backend/README.md) : lancement du backend et manipulation des données côté API.
- [database/README.md](database/README.md) : rôle de la base, migrations, seeds et données historiques.
- [ingestion/README.md](ingestion/README.md) : état actuel de la stack Airbyte/dbt/Prefect et modes d'exécution.
- [ml-image/README.md](ml-image/README.md) : installation et prérequis du pipeline ML image.

Documentation transverse :
- [docs/repo-documentation-guidelines.md](docs/repo-documentation-guidelines.md) : standard documentaire du repository.
- [docs/repo-setup.md](docs/repo-setup.md) : installation des outils système utiles.
- [docs/runbooks/ingestion-runbook-infra-setup-dbt-core-airbyte-remote-postgres.md](docs/runbooks/ingestion-runbook-infra-setup-dbt-core-airbyte-remote-postgres.md) : setup et exploitation infra pour ingestion.
- [docs/specifications/ingestion-specification-airbyte-dbt-mises-a-jour-donnees.md](docs/specifications/ingestion-specification-airbyte-dbt-mises-a-jour-donnees.md) : contrat cible pour les données CNC et corrections métier.
- [docs/architecture/ingestion-architecture-airbyte-dbt-prefect-scraping.md](docs/architecture/ingestion-architecture-airbyte-dbt-prefect-scraping.md) : document unique d'architecture ingestion, avec schéma cible, état relatif et roadmap.
- [docs/architecture/ml-image-architecture-description-pipeline-phase-1.md](docs/architecture/ml-image-architecture-description-pipeline-phase-1.md) : description du pipeline ML phase 1.

## Points D'Attention

- Certains documents de `docs/architecture/` et `docs/specifications/` sont en `draft` ; les lire comme cible ou proposition, pas comme vérité opérationnelle automatique.
- Le backend lit encore les tables applicatives historiques `ric_*` dans plusieurs flux ; ne pas supposer une bascule complète vers la cible Airbyte/dbt.
- Le scraping Allociné existe sous forme historique CSV et sous forme de job standalone dans `ingestion/`.
- Le contenu ML et le contenu ingestion ont des prérequis plus lourds que le frontend/backend ; vérifier avant exécution.

## Résumé Rapide

- Commencer par `README.md`.
- Lire la doc locale du composant avant de coder.
- Mettre à jour la doc dans la même PR.
- Respecter le format de métadonnées et l'historique des fichiers `.md`.
- Utiliser `docs/` pour l'architecture, la spec, les runbooks et les bonnes pratiques.
