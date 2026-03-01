Created by: Hugo Laurens, Joel Teixeira

Last reviewed: 2026-03-01

Status: draft

# Gouvernance Google Sheets pour mises à jour de données

## 1. Objectif

Définir des règles simples pour que les équipes non techniques puissent saisir des mises à jour fiables, exploitables automatiquement, et auditables.

## 2. Documents concernés

1. `AGREEMENT CNC`
2. `Modification data`

## 3. Rôles et responsabilités

1. **Éditeurs métier**:
   - ajoutent ou corrigent des lignes selon le template;
   - renseignent `requested_by` et `modification_date`.
2. **Référent data**:
   - maintient le template;
   - valide les évolutions de schéma;
   - suit les rejets.
3. **Product manager**:
   - arbitre les priorités de correction;
   - coordonne la recette métier.

## 4. Règles de structure

## 4.1 `AGREEMENT CNC`

1. un onglet par année (`2024`, `2025`, `2026`, etc.);
2. colonnes figées selon le dictionnaire validé;
3. `visa_number` obligatoire.

## 4.2 `Modification data`

1. un onglet par entité (`CreditHolder`, `Film`, etc.);
2. colonnes obligatoires:
   - `id`
   - `column_name`
   - `new_value`
   - `modification_date`
   - `requested_by`
3. colonne optionnelle:
   - `reason`

## 5. Règles de saisie

1. ne pas renommer les colonnes;
2. ne pas changer l'ordre des colonnes;
3. ne pas fusionner de cellules;
4. ne pas insérer de lignes d'en-tête supplémentaires;
5. dates au format ISO `YYYY-MM-DD`;
6. `requested_by` au format `prenom.nom` ou adresse email interne.

## 6. Validations Google Sheets recommandées

1. listes déroulantes pour `column_name` par onglet (whitelist);
2. validation date stricte pour `modification_date`;
3. format numérique pour `id`;
4. mise en évidence des cellules vides obligatoires;
5. protection des en-têtes et des colonnes techniques.

## 7. Gestion des accès

1. édition limitée au groupe métier autorisé;
2. lecture possible pour parties prenantes élargies;
3. aucun partage "public internet";
4. compte de service Airbyte en lecture seule.

## 8. Convention de nommage

1. nom des onglets CNC: `YYYY`;
2. nom des onglets corrections: nom exact de l'entité (`CreditHolder`, `Film`);
3. pas d'espaces de fin, pas d'accents variables dans les noms techniques.

## 9. Processus de changement du template

1. toute nouvelle colonne passe d'abord en revue Data + Product;
2. mise à jour du dictionnaire de données dans le repo;
3. recette sur environnement de test avant production;
4. communication aux éditeurs métier.

## 10. Processus en cas d'erreur de saisie

Sans colonne `status` en V1:

1. ne pas supprimer la ligne erronée;
2. ajouter une nouvelle ligne corrective avec:
   - même `id`,
   - même `column_name`,
   - `new_value` corrigée,
   - `reason` explicite (`annulation`, `correction saisie`, etc.),
   - nouvelle `modification_date`.

Règle d'application côté pipeline:

1. la correction valide la plus récente s'applique.

## 11. Contrôles opérationnels hebdomadaires

1. vérifier les rejets de pipeline;
2. vérifier les lignes sans `requested_by`;
3. vérifier les colonnes non autorisées demandées;
4. suivre les délais entre demande et visibilité en production.

## 12. KPI de gouvernance à suivre

1. nombre de corrections saisies par semaine;
2. taux de corrections rejetées;
3. délai médian de prise en compte;
4. top 5 des motifs de rejet.

## 13. Annexes à préparer

1. template Google Sheets verrouillé;
2. dictionnaire de données (colonnes, type, règles);
3. guide rapide "Comment corriger une donnée en 2 minutes".

