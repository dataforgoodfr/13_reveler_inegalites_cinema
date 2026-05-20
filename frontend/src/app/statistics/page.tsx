import type { Metadata } from "next";
import StatisticsClient from "./StatisticsClient";
import { STATISTICS_KEYWORDS } from "@/lib/seo";

export const metadata: Metadata = {
  title: "Statistiques",
  description:
    "Visualisez les statistiques agrégées sur la parité dans le cinéma : budgets, genres, équipes techniques, récompenses. Tableau de bord interactif sur 20 ans de données.",
  keywords: STATISTICS_KEYWORDS,
};

export default function Page() {
  return <StatisticsClient />;
}
