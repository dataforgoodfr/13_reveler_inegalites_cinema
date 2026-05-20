import type { Metadata } from "next";
import { Film } from "@/dto/film/film.dto";
import { Festival } from "@/dto/festival/festival.dto";
import { nameToUpperCase } from "@/utils/name-to-uppercase";

export const SITE_NAME = "CinéStats 50/50";

export const SITE_DESCRIPTION =
  "CinéStats 50/50 : observatoire data-driven des inégalités de parité dans l'industrie cinématographique. Films, festivals, équipes techniques et statistiques détaillées.";

export const DEFAULT_KEYWORDS = [
  "cinéma",
  "inégalités",
  "parité",
  "femmes cinéma",
  "Collectif 50/50",
  "Data for Good",
  "statistiques cinéma",
  "industrie cinématographique",
  "réalisatrices",
  "diversité audiovisuel",
];

export const HOME_KEYWORDS = [
  ...DEFAULT_KEYWORDS,
  "observatoire cinéma",
  "égalité femmes hommes cinéma",
  "représentation cinéma",
  "base de données films",
];

export const STATISTICS_KEYWORDS = [
  ...DEFAULT_KEYWORDS,
  "statistiques parité cinéma",
  "données cinéma",
  "analyse inégalités industrie film",
  "dashboard cinéma",
  "tendances cinéma 50/50",
];

export const ABOUT_KEYWORDS = [
  ...DEFAULT_KEYWORDS,
  "à propos CinéStats",
  "mission Collectif 50/50",
  "projet Data for Good cinéma",
  "observatoire inclusif",
];

const formatDirectors = (film: Film): string => {
  const directors = film.credits?.key_roles?.filter(
    (credit) => credit.role?.toLowerCase().includes("réalis")
  );
  if (!directors || directors.length === 0) return "";
  return directors
    .slice(0, 3)
    .map((d) => nameToUpperCase(d.name))
    .join(", ");
};

const getYear = (dateStr?: string): string => {
  if (!dateStr) return "";
  const year = new Date(dateStr).getFullYear();
  return Number.isNaN(year) ? "" : String(year);
};

export const buildFilmMetadata = (film: Film): Metadata => {
  const year = getYear(film.release_date);
  const directors = formatDirectors(film);
  const genres = film.genres?.slice(0, 3).join(", ") ?? "";

  const title = year
    ? `${film.original_name} (${year})`
    : film.original_name;

  const descriptionParts: string[] = [`Découvrez ${film.original_name}`];
  if (year) descriptionParts[0] += ` (${year})`;
  if (directors) descriptionParts.push(`réalisé par ${directors}`);
  if (genres) descriptionParts.push(`Genre : ${genres}`);
  descriptionParts.push(
    `Analyse de la parité dans l'équipe et la distribution sur ${SITE_NAME}.`
  );
  const description = descriptionParts.join(". ");

  return {
    title,
    description,
  };
};

export const buildFestivalMetadata = (
  festival: Festival,
  year?: number
): Metadata => {
  const title = year ? `${festival.name} ${year}` : festival.name;
  const description =
    festival.description?.trim() ||
    `Découvrez le palmarès et les statistiques de parité du festival ${festival.name}. Films primés, nominations et analyse des inégalités sur ${SITE_NAME}.`;

  return {
    title,
    description,
  };
};
