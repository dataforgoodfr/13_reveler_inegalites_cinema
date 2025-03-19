"use client";

import { useParams } from "next/navigation";

// Ceci est un composant de page avec une route dynamique
// Le [slug] dans le nom du dossier sera disponible comme paramètre
export default function PageFilm() {
  // useParams est un hook qui permet d'accéder aux paramètres dynamiques de l'URL
  const params = useParams();
  const slug = params.slug; // Contient la valeur dynamique de l'URL (ex: pour /films/avatar, slug = "avatar")

  return (
    <main className="min-h-screen p-8">
      <h1 className="text-2xl font-bold mb-4">Détails du Film</h1>
      <p>Identifiant du film : {slug}</p>
      {/* Ajoutez ici le contenu détaillé du film */}
    </main>
  );
}

// Note: Dans Next.js 13+ avec le répertoire app :
// - Les fichiers nommés page.tsx dans un dossier deviennent automatiquement des routes
// - Le dossier [slug] crée un segment de route dynamique
// - Le paramètre sera accessible via le hook useParams()
