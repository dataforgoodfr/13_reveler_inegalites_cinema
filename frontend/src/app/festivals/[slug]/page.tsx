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
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

// Ceci est un composant de page avec une route dynamique
// Le [slug] dans le nom du dossier sera disponible comme paramètre
export default function PageFilm() {
  // useParams est un hook qui permet d'accéder aux paramètres dynamiques de l'URL
  const params = useParams();
  const slug = params?.slug; // Contient la valeur dynamique de l'URL (ex: pour /films/avatar, slug = "avatar")
  const [festivalData, setFestivalData] = useState<any>(null);
  const [awardsData, setAwardsData] = useState<any>(null);
  const [selectedYear, setSelectedYear] = useState<number | null>(null);
  const [selectedAward, setSelectedAward] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [activeSection, setActiveSection] = useState("Gagnants");

  useEffect(() => {
    const url = `http://localhost:5001/festivals/${slug}`;
    fetch(url)
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error("Fetch error");
        }
      })
      .then((value) => {
        setAwardsData(value.festival.awards);
        setFestivalData(value.festival.festival);
        setIsLoading(false);
      })
      .catch((error) => {
        console.error("Erreur lors de la récupération des données :", error);
        setHasError(true);
        setIsLoading(false);
      });
  }, [slug]);

  function getFilteredNominations() {
    const currentSelectedYear = selectedYear;
    const currentSelectedAward = selectedAward;
    if (!currentSelectedAward || !currentSelectedYear) {
      return [];
    }
    return awardsData
      .filter((award: any) => award.award_id === currentSelectedAward)
      .flatMap((award: any) => award.nominations)
      .filter(
        (nomination: any) =>
          new Date(nomination.date).getFullYear() == currentSelectedYear
      );
  }

  if (isLoading || !festivalData || !awardsData) {
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
    <main className="p-20 bg-zinc-800 text-white">
      <div className="flex flex-col items-center md:items-start md:flex-row gap-10">
        <div className="flex flex-col gap-10">
          <img
            style={{ height: "fit-content" }}
            src={festivalData.image_base64}
            alt="Affiche"
            width={257.45}
          />
          <Card className="md:w-[220px] bg-gray-950 border-0">
            <CardHeader>
              <CardDescription className="text-white">
                {festivalData.description}
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
        <div className="w-full">
          <h1 className="text-4xl font-bold mb-4">{festivalData.name}</h1>
          <div>
            <p>Année de l'édition</p>
            <Select onValueChange={(value) => setSelectedYear(parseInt(value))}>
              <SelectTrigger className="w-[180px] bg-white text-black">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  {[
                    ...new Set<number>(
                      awardsData
                        .flatMap((award: any) => award.nominations)
                        .map((nomination: any) =>
                          new Date(nomination.date).getFullYear()
                        )
                    ),
                  ].map((year: number, index: number) => (
                    <SelectItem key={index} value={year.toString()}>
                      {year}
                    </SelectItem>
                  ))}
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>
          {selectedYear && (
            <>
              <div className="flex gap-5 py-5">
                <Card
                  className="md:w-1/2"
                  style={{
                    borderColor: "rgba(51, 51, 51, 1)",
                    backgroundColor: "rgba(30, 30, 30, 0.8)",
                  }}
                >
                  <CardHeader>
                    <CardTitle className="text-2xl text-violet-300">
                      {festivalData.festival_metrics.parity_comparison
                        ? `${festivalData.festival_metrics.parity_comparison.place}ème/${festivalData.festival_metrics.parity_comparison.total}`
                        : "NC"}
                    </CardTitle>
                    <CardDescription className="text-white">
                      en parité comparé à l’ensemble des festivals disponibles
                    </CardDescription>
                  </CardHeader>
                </Card>
                <Card
                  className="md:w-1/3"
                  style={{
                    borderColor: "rgba(51, 51, 51, 1)",
                    backgroundColor: "rgba(30, 30, 30, 0.8)",
                  }}
                >
                  <CardHeader>
                    <CardTitle className="text-2xl text-violet-300">
                      {festivalData.festival_metrics.prizes_awarded_to_women
                        ? `${festivalData.festival_metrics.prizes_awarded_to_women} %`
                        : "NC"}
                    </CardTitle>
                    <CardDescription className="text-white">
                      des prix ont été attribués à des films réalisés par des{" "}
                      <span className="font-bold text-violet-300">femmes</span>
                    </CardDescription>
                  </CardHeader>
                </Card>
                <Card
                  className="md:w-1/3"
                  style={{
                    borderColor: "rgba(51, 51, 51, 1)",
                    backgroundColor: "rgba(30, 30, 30, 0.8)",
                  }}
                >
                  <CardHeader>
                    <CardTitle className="text-2xl text-violet-300">
                      {festivalData.festival_metrics.produced_by_women
                        ? `${festivalData.festival_metrics.produced_by_women} %`
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
                  onValueChange={(value) => setSelectedAward(parseInt(value))}
                >
                  <SelectTrigger className="w-[180px] bg-white text-black">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectGroup>
                      {awardsData
                        .map((award: any) => {
                          return {
                            ...award,
                            nominations: award.nominations.filter(
                              (nomination: any) =>
                                new Date(nomination.date).getFullYear() ===
                                selectedYear
                            ),
                          };
                        })
                        .filter((award: any) => award.nominations.length > 0)
                        .map((award: any, index: number) => (
                          <SelectItem
                            key={index}
                            value={award.award_id.toString()}
                          >
                            {award.name}
                          </SelectItem>
                        ))}
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
                    {getFilteredNominations().filter(
                      (nomination: any) =>
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
                      getFilteredNominations()
                        .filter(
                          (nomination: any) =>
                            nomination.is_winner ===
                            (activeSection === "Gagnants")
                        )
                        .map(({ film }: any, index: number) => (
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
                                backgroundImage: `url(${film.poster_image_base64})`,
                                backgroundSize: "cover",
                                backgroundPosition: "center",
                                backgroundRepeat: "no-repeat",
                                zIndex: 0,
                              }}
                            ></div>
                            <div
                              className="absolute inset-0"
                              style={{
                                backgroundColor: "rgba(0, 0, 0, 0.5)",
                              }}
                            ></div>
                            <div className="z-1 mt-4 flex flex-row gap-10">
                              <img
                                style={{ height: "fit-content" }}
                                src={film.poster_image_base64}
                                alt="Affiche"
                                width={150}
                              />
                              <div className="text-white w-full">
                                <a href={`/films/${film.id}`}>
                                  <strong className="text-2xl">
                                    {film.original_name}
                                  </strong>
                                </a>
                                <p>
                                  Réalisé par <strong>{film.director}</strong>
                                </p>
                                <div className="flex flex-col md:flex-row gap-5">
                                  {film.female_representation_in_key_roles ||
                                  film.female_representation_in_casting ? (
                                    <>
                                      <Card
                                        className="md:w-[220px]"
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
                                        className="md:w-[220px]"
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

// Note: Dans Next.js 13+ avec le répertoire app :
// - Les fichiers nommés page.tsx dans un dossier deviennent automatiquement des routes
// - Le dossier [slug] crée un segment de route dynamique
// - Le paramètre sera accessible via le hook useParams()
