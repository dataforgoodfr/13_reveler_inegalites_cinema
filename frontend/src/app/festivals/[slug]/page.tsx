"use client";

import { useEffect, useState } from "react";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Menubar, MenubarMenu, MenubarTrigger } from "@/components/ui/menubar";
import { useParams } from "next/navigation";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { FestivalApiResponse } from "@/dto/festival/festival-api-response.dto";
import { Nomination } from "@/dto/festival/nomination.dto";
import Link from "next/link";
import Image from "next/image";
import { API_URL } from "@/utils/api-url";
import { ReducedAward } from "@/dto/festival/reduced-award.dto";
import { nameToUpperCase } from "@/utils/name-to-uppercase";

// Ceci est un composant de page avec une route dynamique
// Le [slug] dans le nom du dossier sera disponible comme paramètre
export default function PageFilm() {
  // useParams est un hook qui permet d'accéder aux paramètres dynamiques de l'URL
  const params = useParams();
  const slug = params?.slug; // Contient la valeur dynamique de l'URL (ex: pour /films/avatar, slug = "avatar")
  const [festivalData, setFestivalData] = useState<FestivalApiResponse | null>(
    null
  );
  const [selectedYear, setSelectedYear] = useState<number | null>(null);
  const [selectedAward, setSelectedAward] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [activeSection, setActiveSection] = useState("Gagnants");

  useEffect(() => {
    const baseUrl = `${API_URL}/festivals/${slug}`;
    const queryParams = new URLSearchParams();

    if (selectedYear !== null) {
      queryParams.append("year", selectedYear.toString());
    }
    if (selectedAward !== null) {
      queryParams.append("award", selectedAward.toString());
    }

    const url = `${baseUrl}?${queryParams.toString()}`;
    fetch(url)
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error("Fetch error");
        }
      })
      .then((value: FestivalApiResponse) => {
        setFestivalData(value);
        setSelectedYear(value.year);
        // Ne définir selectedAward que si elle n'est pas déjà définie
        if (selectedAward === null) {
          setSelectedAward(value.award.award_id);
        }
        setIsLoading(false);
      })
      .catch((error) => {
        console.error("Erreur lors de la récupération des données :", error);
        setHasError(true);
        setIsLoading(false);
      });
  }, [selectedAward, selectedYear, slug]);

  if (isLoading || !festivalData) {
    return (
      <main className="p-20 bg-transparent text-white flex justify-center items-center">
        <p>Chargement...</p>
      </main>
    );
  }

  if (hasError) {
    return (
      <main className="p-20 bg-transparent text-white flex justify-center items-center">
        <h1 className="text-4xl font-bold">404 - Festival non trouvé</h1>
      </main>
    );
  }

  return (
    <main className="p-5 pt-20 bg-zinc-800 text-white min-h-screen">
      <div className="flex flex-col md:items-start md:flex-row gap-10">
        <div className="flex flex-col gap-10 w-full md:w-1/4">
          {festivalData.festival.image_base64 &&
          festivalData.festival.image_base64.trim() !== "" ? (
            <Image
              loader={() => festivalData.festival.image_base64}
              style={{ height: "fit-content" }}
              src={festivalData.festival.image_base64.trim()}
              alt="Affiche"
              width={300}
              height={0}
            />
          ) : (
            <Image
              style={{ height: "fit-content" }}
              src="/placeholder_image.svg"
              alt="Image indisponible"
              width={300}
              height={0}
            />
          )}
          <h1 className="md:hidden text-4xl font-bold">
            {festivalData.festival.name}
          </h1>

          {festivalData.festival.description && (
            <Card className="bg-gray-950 border-0">
              <CardHeader>
                <CardDescription className="text-white">
                  {festivalData.festival.description}
                </CardDescription>
              </CardHeader>
            </Card>
          )}
        </div>
        <div className="md:w-3/4">
          <h1 className="hidden md:block text-4xl font-bold mb-4">
            {festivalData.festival.name}
          </h1>
          <div>
            <p>Année de l&apos;édition</p>
            <Select
              value={selectedYear ? selectedYear.toString() : undefined}
              onValueChange={(value: string) => {
                setSelectedYear(parseInt(value));
                setSelectedAward(null);
              }}
            >
              <SelectTrigger className="w-[180px] bg-white text-black">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  {festivalData.available_years.map(
                    (year: number, index: number) => (
                      <SelectItem key={index} value={year.toString()}>
                        {year}
                      </SelectItem>
                    )
                  )}
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>
          {selectedYear && (
            <>
              <div className="flex flex-col md:flex-row gap-5 py-5">
                <Card
                  className="w-full md:w-1/2"
                  style={{
                    borderColor: "rgba(51, 51, 51, 1)",
                    backgroundColor: "rgba(30, 30, 30, 0.8)",
                  }}
                >
                  <CardHeader>
                    <CardTitle className="text-2xl text-violet-300">
                      {typeof festivalData.festival.festival_metrics
                        .female_representation_in_award_winning_films ==
                      "number"
                        ? `${festivalData.festival.festival_metrics.female_representation_in_award_winning_films} %`
                        : "NC"}
                    </CardTitle>
                    <CardDescription className="text-white">
                      des prix ont été attribués à des films réalisés par des{" "}
                      <span className="font-bold text-violet-300">femmes</span>
                    </CardDescription>
                  </CardHeader>
                </Card>
                <Card
                  className="w-full md:w-1/2"
                  style={{
                    borderColor: "rgba(51, 51, 51, 1)",
                    backgroundColor: "rgba(30, 30, 30, 0.8)",
                  }}
                >
                  <CardHeader>
                    <CardTitle className="text-2xl text-violet-300">
                      {typeof festivalData.festival.festival_metrics
                        .female_representation_in_nominated_films == "number"
                        ? `${festivalData.festival.festival_metrics.female_representation_in_nominated_films} %`
                        : "NC"}
                    </CardTitle>
                    <CardDescription className="text-white">
                      des films sélectionnés ont été réalisés par des{" "}
                      <span className="font-bold text-violet-300">femmes</span>
                    </CardDescription>
                  </CardHeader>
                </Card>
              </div>
              <div>
                <p>Récompense</p>
                <Select
                  value={selectedAward ? selectedAward.toString() : undefined}
                  onValueChange={(value: string) =>
                    setSelectedAward(parseInt(value))
                  }
                >
                  <SelectTrigger className="w-full md:w-[250px] bg-white text-black wordbreak">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="w-full md:w-[250px] wordbreak">
                    <SelectGroup>
                      {festivalData.available_awards.map(
                        (award: ReducedAward, index: number) => (
                          <SelectItem
                            key={index}
                            value={award.award_id.toString()}
                          >
                            {award.name}
                          </SelectItem>
                        )
                      )}
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </div>
              {typeof selectedAward === "number" && (
                <div className="mt-8 flex flex-col gap-5">
                  <Menubar className="w-fit text-black">
                    <MenubarMenu>
                      <MenubarTrigger
                        onClick={() => setActiveSection("Gagnants")}
                      >
                        Gagnants
                      </MenubarTrigger>
                    </MenubarMenu>
                    <MenubarMenu>
                      <MenubarTrigger
                        onClick={() => setActiveSection("Nommés")}
                      >
                        Nommés
                      </MenubarTrigger>
                    </MenubarMenu>
                  </Menubar>

                  <div className="flex flex-col gap-5">
                    {festivalData.award.nominations.filter(
                      (nomination: Nomination) =>
                        nomination.is_winner === (activeSection === "Gagnants")
                    ).length === 0 ? (
                      <Card
                        className="relative border-violet-700 p-5"
                        style={{
                          position: "relative",
                          overflow: "hidden",
                          backgroundColor: "rgba(30, 30, 30, 0.8)",
                        }}
                      >
                        <CardHeader>
                          <CardDescription className="text-xl text-white">
                            Aucune donnée disponible pour cette section.
                          </CardDescription>
                        </CardHeader>
                      </Card>
                    ) : (
                      festivalData.award.nominations
                        .filter(
                          (nomination: Nomination) =>
                            nomination.is_winner ===
                            (activeSection === "Gagnants")
                        )
                        .map(({ film }: Nomination, index: number) => (
                          <Card
                            key={index}
                            className="relative border-violet-700 p-5"
                            style={{
                              position: "relative",
                              overflow: "hidden",
                            }}
                          >
                            <div
                              className="absolute inset-0"
                              style={{
                                backgroundImage:
                                  film.poster_image_base64 &&
                                  film.poster_image_base64.trim() !== ""
                                    ? `url(${film.poster_image_base64})`
                                    : "url(/placeholder_image.svg)",
                                backgroundSize: "cover",
                                backgroundPosition: "center",
                                backgroundRepeat: "no-repeat",
                                zIndex: 0,
                                backgroundColor: "#27272a",
                              }}
                            ></div>
                            <div
                              className="absolute inset-0"
                              style={{
                                backgroundColor: "rgba(0, 0, 0, 0.5)",
                              }}
                            ></div>
                            <div className="z-1 mt-4 flex flex-row gap-10 overflow-x-auto">
                              {film.poster_image_base64 &&
                              film.poster_image_base64.trim() !== "" ? (
                                <Image
                                  loader={() => film.poster_image_base64}
                                  style={{ height: "fit-content" }}
                                  src={film.poster_image_base64.trim()}
                                  alt="Affiche"
                                  width={150}
                                  height={0}
                                />
                              ) : (
                                <Image
                                  style={{ height: "fit-content" }}
                                  src="/placeholder_image.svg"
                                  alt="Image indisponible"
                                  width={150}
                                  height={0}
                                />
                              )}
                              <div className="text-white w-full overflow-x-auto">
                                <Link href={`/films/${film.id}`}>
                                  <strong className="text-2xl">
                                    {film.original_name}
                                  </strong>
                                </Link>
                                <p>
                                  Réalisé par{" "}
                                  <strong>
                                    {film.director
                                      .map(nameToUpperCase)
                                      .join(", ")}
                                  </strong>
                                </p>
                                <div className="flex flex-row gap-5 max-w-full overflow-x-auto">
                                  {film.female_representation_in_key_roles ||
                                  film.female_representation_in_casting ? (
                                    <>
                                      <Card
                                        className="min-w-[160px] w-[220px] md:w-1/2"
                                        style={{
                                          borderColor: "rgba(51, 51, 51, 1)",
                                          backgroundColor:
                                            "rgba(30, 30, 30, 0.8)",
                                        }}
                                      >
                                        <CardHeader>
                                          <CardTitle className="text-2xl text-violet-300">
                                            {film.female_representation_in_key_roles
                                              ? `${film.female_representation_in_key_roles} %`
                                              : "NC"}
                                          </CardTitle>
                                          <CardDescription className="text-white">
                                            de femmes au sein des{" "}
                                            <span className="font-bold text-violet-300">
                                              cheffes de postes
                                            </span>
                                          </CardDescription>
                                        </CardHeader>
                                      </Card>
                                      <Card
                                        className="min-w-[160px] w-[220px] md:w-1/2"
                                        style={{
                                          borderColor: "rgba(51, 51, 51, 1)",
                                          backgroundColor:
                                            "rgba(30, 30, 30, 0.8)",
                                        }}
                                      >
                                        <CardHeader>
                                          <CardTitle className="text-2xl text-violet-300">
                                            {film.female_representation_in_casting
                                              ? `${film.female_representation_in_casting} %`
                                              : "NC"}
                                          </CardTitle>
                                          <CardDescription className="text-white">
                                            de femmes dans{" "}
                                            <span className="font-bold text-violet-300">
                                              le casting principal
                                            </span>
                                          </CardDescription>
                                        </CardHeader>
                                      </Card>
                                    </>
                                  ) : (
                                    <Card
                                      className="w-full"
                                      style={{
                                        borderColor: "rgba(51, 51, 51, 1)",
                                        backgroundColor:
                                          "rgba(30, 30, 30, 0.8)",
                                      }}
                                    >
                                      <CardHeader>
                                        <CardTitle className="text-violet-300">
                                          Aucune donnée disponible pour ce film
                                        </CardTitle>
                                      </CardHeader>
                                    </Card>
                                  )}
                                </div>
                              </div>
                            </div>
                          </Card>
                        ))
                    )}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </main>
  );
}
