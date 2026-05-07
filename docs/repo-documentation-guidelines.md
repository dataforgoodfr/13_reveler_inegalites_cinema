**Owner:** Joel Teixeira

**Last reviewed:** 2026-05-07

**Status:** active

## Historique du document

| Date       | Author         | Observations                                                             |
|------------|----------------|--------------------------------------------------------------------------|
| 2026-05-07 | Joel Teixeira  | Traduction française, ajout du template et normalisation des métadonnées |

# Guide Général De Documentation

Ce guide définit un standard pratique pour créer, rédiger, mettre à jour et maintenir la documentation d'un projet dans n'importe quel dépôt logiciel.

## 1. Objectifs

La documentation doit être :
- Utile : aide quelqu'un à accomplir une tâche réelle.
- Exacte : correspond au comportement actuel du système.
- Facile à trouver : simple à localiser et à parcourir.
- Maintenable : dispose d'un responsable clair et d'une fréquence de revue définie.

## 2. Ensemble Minimal De Documentation

Chaque projet devrait avoir :
- Un `README.md` à la racine.
- Un `README.md` par service/composant.
- Un répertoire `docs/` organisé par catégorie de documentation.

### 2.1 README.md Racine (niveau projet)

Inclure au minimum :
1. L'objectif et le périmètre.
2. Une vue d'ensemble de l'architecture.
3. La structure du dépôt.
4. Un démarrage rapide (exécution locale).
5. Une vue d'ensemble du déploiement.
6. Les points d'entrée pour le debug / dépannage.
7. Les commandes de test et de validation.
8. Les liens vers la documentation détaillée.

### 2.2 README.md De Service (niveau service)

Chaque service devrait inclure :
1. L'objectif du service et ses responsabilités.
2. La structure des répertoires / modules.
3. La configuration et les variables d'environnement.
4. Comment l'exécuter en local.
5. Comment le déployer.
6. Comment le débugger (logs, health checks, échecs courants).
7. La stratégie de test et les commandes principales.
8. Les dépendances et intégrations.

## 3. Taxonomie Recommandée Pour `docs/`

Catégories principales :
- `docs/specifications/`
- `docs/guidelines-best-practices/`
- `docs/improvement-recommendations/`
- `docs/architecture/`
- `docs/expertise/`

Catégories additionnelles utiles :
- `docs/runbooks/` (opérations, incidents, reprise)
- `docs/reference/` (API, schémas, contrats)
- `docs/adr/` (architecture decision records)
- `docs/templates/` (modèles de documentation réutilisables)

## 4. Cycle De Vie D'Un Document

### 4.1 Création

Créer un nouveau document quand :
- Une nouvelle fonctionnalité ou un nouveau workflow est introduit.
- Un comportement change d'une manière sur laquelle les utilisateurs/développeurs s'appuient.
- Un problème récurrent de support / debug apparaît.
- Une décision d'architecture ou produit importante est prise.

Métadonnées requises en haut de chaque document :
- `Owner`
- `Last reviewed`
- `Status` (`draft`, `active`, `deprecated`, `obsolete`)
- Un historique du document, de préférence sous forme de tableau avec les colonnes `Date`, `Author`, `Observations`

### 4.2 Rédaction

Règles d'écriture :
- Commencer par l'objectif, puis les prérequis, puis les étapes.
- Préférer des titres orientés tâches (`Comment...`, `Dépannage...`).
- Garder une langue directe et sans ambiguïté.
- Utiliser des exemples pour les commandes, requêtes et configurations.
- Éviter le jargon interne sauf s'il est défini dans un glossaire.
- Écrire la documentation en français chaque fois que possible, surtout pour les contenus internes et destinés à l'équipe.

Règles de sécurité et de confidentialité :
- Ne jamais inclure de secrets, identifiants, tokens ou clés privées.
- Masquer les valeurs sensibles dans les exemples.
- Ne pas inclure de données personnelles ou de données permettant d'identifier un client, sauf autorisation explicite.

### 4.3 Modification / Mise À Jour

Lors d'un changement de comportement dans le code :
- Mettre à jour la documentation pertinente dans la même PR chaque fois que possible.
- Si ce n'est pas possible, créer un suivi tracé avec responsable et date d'échéance.

Pour les mises à jour :
- Garder un historique utile (`Ce qui a changé` et `Pourquoi`).
- Mettre à jour l'historique du document à chaque modification significative.
- Marquer le contenu obsolète avec des consignes de migration.
- Déplacer le contenu périmé vers un dossier d'archives.

### 4.4 Maintenance

Fréquence de maintenance :
- Docs critiques (runbooks, déploiement, sécurité) : revue mensuelle.
- Docs techniques actives : revue trimestrielle.
- Docs de référence long terme : revue tous les 6 mois.

Exigences de maintenance :
- Chaque document doit avoir un responsable ou une équipe nommée.
- Les liens cassés et commandes obsolètes doivent être corrigés rapidement.
- Les docs dépassées doivent être corrigées, dépréciées ou archivées.

## 5. Standards De Qualité

Un document est complet quand il est :
- Correct : validé par rapport au comportement actuel.
- Actionnable : contient assez d'étapes pour être exécuté.
- Ciblé : concentré sur un seul sujet.
- Lié : référence la documentation associée.
- Testable : les exemples / commandes peuvent être exécutés.

Éviter :
- Les duplications par copier-coller dans plusieurs documents.
- Les gros documents mélangeant plusieurs sujets.
- Les mots ambigus comme "bientôt", "généralement", "parfois".
- Les documents sans responsable ou sans date.

## 6. Versionnement Et Nommage

Conventions de nommage :
- Utiliser des noms de fichiers clairs, stables, en kebab-case.
- Les documents spécifiques doivent commencer par un préfixe de module ou domaine en kebab-case, afin de rendre leur portée immédiatement visible.
- Garder un seul sujet par fichier.
- Préférer des noms explicites aux noms génériques (`api-authentication.md` plutôt que `notes.md`).

Exemple :
- `ingestion-spec-airbyte-dbt-prefect-modifications-donnees.md`

Conventions de versionnement :
- Versionner les docs qui décrivent des contrats externes (API, schémas, protocoles).
- Conserver des notes de migration quand des changements cassants ont lieu.

## 7. Workflow De Revue Suggéré

Pour chaque PR de documentation :
1. Revue technique par le responsable de la fonctionnalité.
2. Revue de lisibilité par quelqu'un hors implémentation.
3. Validation des liens / commandes.
4. Vérification de la présence des métadonnées (`owner`, `last reviewed`, `status`).

## 8. Modèles (Recommandé)

Utiliser `docs/templates/` pour :
- Le modèle de README racine.
- Le modèle de README de service.
- Le modèle de spécification.
- Le modèle d'architecture.
- Le modèle de runbook.
- Le modèle d'ADR.

Exemple de bloc de métadonnées à placer en haut d'un document :

```md
**Owner:** equipe-data

**Last reviewed:** 2026-05-07

**Status:** active

## Historique du document

| Date       | Author       | Observations                                  |
|------------|--------------|-----------------------------------------------|
| 2026-05-07 | Jane Doe     | Création du document                          |
| 2026-05-10 | John Doe     | Mise à jour du workflow d'ingestion           |
| 2026-05-15 | equipe-data  | Clarifications sur le déploiement et le debug |
```

## 9. Recommandations D'Automatisation

Utiliser des vérifications CI pour imposer la qualité documentaire :
- Lint Markdown.
- Vérification des liens.
- Vérification orthographique.
- Vérification optionnelle de couverture documentaire (ex. : chaque service doit avoir un `README.md`).
- Alertes optionnelles sur les docs obsolètes selon la date `Last reviewed`.

## 10. Recommandations De Gouvernance

Pour garder une documentation complète dans la durée :
- Définir un responsable documentation par service.
- Rendre "impact documentation" obligatoire dans la checklist de PR.
- Inclure la revue documentaire dans les vérifications de release readiness.
- Réaliser des audits et nettoyages documentaires périodiques.
- Traiter la documentation comme un produit : mesurable, revue et améliorée en continu.
