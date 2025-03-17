# Objectif 50 / 50 frontend

## Prérequis

- Node.js (v20 ou plus récent)
- pnpm (Gestionnaire de paquets)

## Installation de pnpm

```bash
# Installer pnpm globalement
npm install -g pnpm

# Vérifier l'installation
pnpm --version
```

## Configuration du Projet

1. Installer les dépendances :
```bash
pnpm install
```

2. Démarrer le serveur de développement :
```bash
pnpm dev
```

L'application sera disponible sur [http://localhost:3000](http://localhost:3000).

## Dépendances du Projet

Les dépendances principales incluent :
- Next.js 15
- React 19
- TypeScript
- TailwindCSS (pour le style)
- shadcn/ui (pour les composants UI)

## Structure du Projet

```
├── app/            # Routes de l'application Next.js
├── components/     # Composants React réutilisables
├── public/         # Ressources statiques
└── styles/        # Styles globaux
```

## Bases de Next.js

Next.js est un framework React qui fournit :
- Rendu côté serveur
- Génération de sites statiques
- Routes API
- Routage basé sur les fichiers
- Optimisation intégrée

### Fonctionnalités Principales
- Les pages sont créées dans le répertoire `app`
- Les routes API sont définies dans `app/api`
- Les ressources statiques vont dans le répertoire `public`
- Fractionnement automatique du code
- Remplacement à chaud des modules

## Guide de Développement

1. Respecter le système de types TypeScript
2. Utiliser des composants pour les éléments UI réutilisables
3. Garder les pages dans le répertoire app
4. Suivre les bonnes pratiques Next.js
5. Utiliser les composants shadcn/ui pour un design cohérent

Pour plus de détails, consultez la [documentation Next.js](https://nextjs.org/docs).
