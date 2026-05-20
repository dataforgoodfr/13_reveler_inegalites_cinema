import type { Metadata } from "next";
import HomeClient from "./HomeClient";
import { HOME_KEYWORDS, SITE_NAME } from "@/lib/seo";

export const metadata: Metadata = {
  title: {
    absolute: `${SITE_NAME} — Inégalités de parité dans l'industrie du cinéma`,
  },
  description:
    "Explorez les inégalités de parité dans le cinéma : recherche par film, données sur les équipes techniques et artistiques, statistiques sur 20 ans. Un projet du Collectif 50/50 et Data for Good.",
  keywords: HOME_KEYWORDS,
};

export default function Page() {
  return <HomeClient />;
}
