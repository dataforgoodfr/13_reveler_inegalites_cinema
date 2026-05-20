import type { Metadata } from "next";
import AboutClient from "./AboutClient";
import { ABOUT_KEYWORDS } from "@/lib/seo";

export const metadata: Metadata = {
  title: "À propos",
  description:
    "Découvrez la mission de CinéStats 50/50 : un observatoire data-driven du Collectif 50/50 et de Data for Good qui mesure les inégalités de parité dans l'industrie cinématographique pour impulser un changement concret.",
  keywords: ABOUT_KEYWORDS,
};

export default function Page() {
  return <AboutClient />;
}
