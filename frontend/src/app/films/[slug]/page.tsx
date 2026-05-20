import type { Metadata } from "next";
import { INTERNAL_API_URL } from "@/utils/api-url";
import { FilmApiResponse } from "@/dto/film/film-api-response.dto";
import { buildFilmMetadata } from "@/lib/seo";
import FilmClient from "./FilmClient";

type PageProps = {
  params: Promise<{ slug: string }>;
};

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const { slug } = await params;

  try {
    const response = await fetch(`${INTERNAL_API_URL}/films/${slug}`);
    if (!response.ok) {
      throw new Error("Fetch error");
    }
    const data: FilmApiResponse = await response.json();
    return buildFilmMetadata(data.film);
  } catch {
    return {
      title: "Film introuvable",
      description:
        "Ce film n'a pas pu être trouvé dans la base CinéStats 50/50.",
    };
  }
}

export default function Page() {
  return <FilmClient />;
}
