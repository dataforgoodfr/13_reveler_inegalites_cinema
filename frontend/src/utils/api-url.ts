export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5001";

// URL utilisée uniquement côté serveur (SSR / generateMetadata) :
// dans un container Docker, `localhost` ne pointe pas vers le backend.
// Fallback sur API_URL pour les environnements sans Docker.
export const INTERNAL_API_URL = process.env.INTERNAL_API_URL ?? API_URL;
