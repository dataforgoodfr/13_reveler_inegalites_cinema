import type { Metadata } from "next";
import { INTERNAL_API_URL } from "@/utils/api-url";
import { FestivalApiResponse } from "@/dto/festival/festival-api-response.dto";
import { buildFestivalMetadata } from "@/lib/seo";
import FestivalClient from "./FestivalClient";

type PageProps = {
  params: Promise<{ slug: string }>;
};

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const { slug } = await params;

  try {
    const response = await fetch(`${INTERNAL_API_URL}/festivals/${slug}`);
    if (!response.ok) {
      throw new Error("Fetch error");
    }
    const data: FestivalApiResponse = await response.json();
    return buildFestivalMetadata(data.festival, data.year);
  } catch {
    return {
      title: "Festival introuvable",
      description:
        "Ce festival n'a pas pu être trouvé dans la base CinéStats 50/50.",
    };
  }
}

export default function Page() {
  return <FestivalClient />;
}
