"use client";

import { useEffect, useRef, useState } from "react";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Menubar, MenubarMenu, MenubarTrigger } from "@/components/ui/menubar";
import { useParams } from "next/navigation";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

import ShareDialog from "@/components/atoms/ShareDialog";
import TrailerAnalysisDialog from "@/components/atoms/TrailerAnalysisDialog";
import PosterAnalysisDialog from "@/components/atoms/PosterAnalysisDialog";
import { t } from "@/utils/i18n";

// Ceci est un composant de page avec une route dynamique
// Le [slug] dans le nom du dossier sera disponible comme paramètre
export default function PageFilm() {
  // useParams est un hook qui permet d'accéder aux paramètres dynamiques de l'URL
  const params = useParams();
  const slug = params?.slug; // Contient la valeur dynamique de l'URL (ex: pour /films/avatar, slug = "avatar")
  const [filmData, setFilmData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [activeSection, setActiveSection] = useState("Statistiques");

  useEffect(() => {
    const url = `http://localhost:5001/films/${slug}`;
    fetch(url)
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error("Fetch error");
        }
      })
      .then((value) => {
        setFilmData(value.film);
        setIsLoading(false);
      })
      .catch(() => {
        setHasError(true);
        setIsLoading(false);
      });
  }, [slug]);

  function getDate(dateStr: string) {
    const date = new Date(dateStr);

    const options: Intl.DateTimeFormatOptions = {
      day: "numeric",
      month: "long",
      year: "numeric",
    };
    return new Intl.DateTimeFormat("fr-FR", options).format(date);
  }

  function groupByCriteria(list: any[], criteria: string) {
    return list.reduce((acc, element) => {
      const data = element[criteria];

      if (!acc[data]) {
        acc[data] = [];
      }

      acc[data].push(element);
      return acc;
    }, {});
  }

  if (isLoading) {
    return (
      <main className="p-20 bg-transparent text-white flex justify-center items-center">
        <p>Chargement...</p>
      </main>
    );
  }

  if (hasError || !filmData) {
    return (
      <main className="p-20 bg-transparent text-white flex justify-center items-center">
        <h1 className="text-4xl font-bold">404 - Film non trouvé</h1>
      </main>
    );
  }

  return (
    <main className="p-20 bg-transparent text-white">
      <div
        className="background-image"
        style={
          {
            "--background-image-url": `url(${filmData.poster_image_base64})`,
          } as React.CSSProperties
        }
      ></div>
      <div className="flex flex-col items-center md:items-start md:flex-row gap-10">
        <div className="relative">
          <img
            style={{ height: "fit-content" }}
            src={filmData.poster_image_base64}
            alt="Affiche"
            width={257.45}
          />
          <div className="absolute flex flex-col gap-2 bottom-2 left-2">
            <PosterAnalysisDialog
              imageSource={filmData.poster_image_base64}
              femaleVisibleRatioOnPoster={
                filmData.metrics.female_visible_ratio_on_poster
              }
              nonWhiteVisibleRatioOnPoster={
                filmData.metrics.non_white_visible_ratio_on_poster
              }
            />
            <TrailerAnalysisDialog
              filmName={filmData.original_name}
              releaseDate={filmData.release_date}
              trailerUrl={filmData.trailer_url}
              femaleScreenTimeInTrailer={
                filmData.metrics.female_screen_time_in_trailer
              }
              nonWhiteScreenTimeInTrailer={
                filmData.metrics.non_white_screen_time_in_trailer
              }
            />
            <ShareDialog imageSource={filmData.poster_image_base64} />
          </div>
        </div>
        <div className="w-full flex md:block flex-col">
          <h1 className="text-4xl font-bold mb-4">
            {filmData.original_name + " "}
            <span className="text-sm">
              ({new Date(filmData.release_date).getFullYear()})
            </span>
          </h1>
          <h2>
            Réalisé par{" "}
            {filmData.credits
              .key_roles
              .filter((c: any) => c.role === "director")
              .map((c: any) => c.name)
              .join(", ")}
          </h2>
          <p className="text-lg mb-2">
            {getDate(filmData.release_date)} en salle {filmData.duration}
          </p>
          <p className="text-lg mb-2">
            Pays d'origine: {filmData.countries_sorted_by_budget.join(", ")}
          </p>
          <div className="flex mb-4 gap-2">
            {filmData.genres.map((genre: string, index: number) => (
              <Badge key={index} className="bg-zinc-700">
                {genre}
              </Badge>
            ))}
          </div>
          <Dialog>
            {filmData.parity_bonus ? (
              <Button className="bg-green-200 hover:bg-green-200 text-green-950 rounded-full">
                Bonus parité du CNC
                <DialogTrigger asChild>
                  <img src="/info.svg" alt="Rechercher" />
                </DialogTrigger>
              </Button>
            ) : (
              <Button className="bg-red-200 hover:bg-red-200 text-red-950 rounded-full">
                Film non éligible au bonus parité du CNC
                <DialogTrigger asChild>
                  <img src="/info.svg" alt="Rechercher" />
                </DialogTrigger>
              </Button>
            )}
            <DialogContent
              className="sm:max-w-[425px] text-white"
              style={{
                borderColor: "rgba(51, 51, 51, 1)",
                backgroundColor: "rgba(30, 30, 30)",
              }}
            >
              <DialogHeader>
                <DialogTitle>Bonus parité du CNC</DialogTitle>
                <DialogDescription className="text-white">
                  Ce bonus de 15% sur le soutien cinéma mobilisé s’adresse aux
                  films d’initiative française dont les équipes sont paritaires
                  au sein de leurs principaux postes d’encadrement, que la
                  réalisation soit entre les mains d’un homme ou d’une femme.
                </DialogDescription>
              </DialogHeader>
            </DialogContent>
          </Dialog>
          <div className="mt-8">
            <Menubar className="w-fit text-black">
              <MenubarMenu>
                <MenubarTrigger
                  onClick={() => setActiveSection("Statistiques")}
                >
                  Statistiques
                </MenubarTrigger>
              </MenubarMenu>
              <MenubarMenu>
                <MenubarTrigger
                  onClick={() => setActiveSection("Distribution")}
                >
                  Distribution
                </MenubarTrigger>
              </MenubarMenu>
              <MenubarMenu>
                <MenubarTrigger
                  onClick={() => setActiveSection("Equipe du film")}
                >
                  Equipe du film
                </MenubarTrigger>
              </MenubarMenu>
              <MenubarMenu>
                <MenubarTrigger onClick={() => setActiveSection("Casting")}>
                  Casting
                </MenubarTrigger>
              </MenubarMenu>
              <MenubarMenu>
                <MenubarTrigger onClick={() => setActiveSection("Palmarès")}>
                  Palmarès
                </MenubarTrigger>
              </MenubarMenu>
            </Menubar>

            {/* Affichage conditionnel des sections */}
            {activeSection === "Statistiques" && (
              <div className="mt-4">
                <div className="flex flex-col md:flex-row gap-5">
                  {filmData.metrics.female_representation_in_key_roles ||
                  filmData.metrics.female_representation_in_casting ? (
                    <>
                      <Card
                        className="md:w-[220px]"
                        style={{
                          borderColor: "rgba(51, 51, 51, 1)",
                          backgroundColor: "rgba(30, 30, 30, 0.8)",
                        }}
                      >
                        <CardHeader>
                          <CardTitle className="text-violet-300">
                            {filmData.metrics.female_representation_in_key_roles
                              ? `${filmData.metrics.female_representation_in_key_roles} %`
                              : "NC"}
                          </CardTitle>
                          <CardDescription className="text-white">
                            de femmes au sein des{" "}
                            <span className="text-violet-300">
                              cheffes de postes
                            </span>
                          </CardDescription>
                        </CardHeader>
                      </Card>
                      <Card
                        className="md:w-[220px]"
                        style={{
                          borderColor: "rgba(51, 51, 51, 1)",
                          backgroundColor: "rgba(30, 30, 30, 0.8)",
                        }}
                      >
                        <CardHeader>
                          <CardTitle className="text-violet-300">
                            {filmData.metrics.female_representation_in_casting
                              ? `${filmData.metrics.female_representation_in_casting} %`
                              : "NC"}
                          </CardTitle>
                          <CardDescription className="text-white">
                            de femmes dans{" "}
                            <span className="text-violet-300">
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
                        backgroundColor: "rgba(30, 30, 30, 0.8)",
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
            )}

            {activeSection === "Distribution" && (
              <>
                {Object.entries(
                  groupByCriteria(
                    filmData.credits.distribution,
                    "role"
                  )
                ).map(([role, credits]: any, role_index: number) => (
                  <div key={role_index} className="mt-4">
                    <span
                      className="block rounded-sm font-bold w-full px-2 py-1"
                      style={{ backgroundColor: "rgba(63, 63, 70, 0.4)" }}
                    >
                      {t(`distribution.${role}`)}
                    </span>
                    <div className="flex">
                      {credits.map((credit: any, index: number) => (
                        <div className="px-2 py-1" key={index}>
                          <Badge className="bg-gray-800">{credit.name}</Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
                <div className="mt-4">
                  <span
                    className="block rounded-sm font-bold w-full px-2 py-1"
                    style={{ backgroundColor: "rgba(63, 63, 70, 0.4)" }}
                  >
                    Budget
                  </span>
                  <div className="px-2 py-1">
                    <span>{filmData.budget.toLocaleString()} €</span>
                  </div>
                </div>
              </>
            )}

            {activeSection === "Equipe du film" && (
              <div
                className="mt-4 grid grid-cols-2"
                style={{
                  columnGap: "80px",
                  rowGap: "24px",
                }}
              >
                {Object.entries(
                  groupByCriteria(
                    filmData.credits.key_roles,
                    "role"
                  )
                ).map(([role_name, roles]: any[], index: number) => (
                  <div
                    key={index}
                    className="flex flex-col"
                    style={{
                      gap: "12px",
                    }}
                  >
                    <div
                      className="rounded-md font-bold"
                      style={{
                        backgroundColor: "rgba(63, 63, 70, 0.4)",
                        padding: "4px 8px",
                      }}
                    >
                      {t(`roles.${role_name}`)}
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {roles.map((role: any, index: number) => (
                        <Badge
                          key={index}
                          className={
                            role.gender === "male"
                              ? "bg-slate-700"
                              : "bg-violet-800"
                          }
                        >
                          {role.name}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeSection === "Casting" && (
              <div className="pt-5 flex flex-wrap gap-2">
                {filmData.credits.casting
                  .map((actor: any, index: number) => (
                    <Badge
                      key={index}
                      className={
                        actor.gender === "male"
                          ? "bg-slate-700"
                          : "bg-violet-800"
                      }
                    >
                      {actor.name}
                    </Badge>
                  ))}
              </div>
            )}

            {activeSection === "Palmarès" && (
              <div
                className="mt-4 flex flex-col"
                style={{
                  gap: "24px",
                }}
              >
                <div
                  className="grid"
                  style={{
                    gap: "12px",
                  }}
                >
                  <div
                    className="rounded-md font-bold"
                    style={{
                      backgroundColor: "rgba(63, 63, 70, 0.4)",
                      padding: "4px 8px",
                    }}
                  >
                    Récompenses
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {filmData.awards
                      .filter((award: any) => award.is_winner)
                      .map((award: any, index: number) => (
                        <Badge key={index} className="bg-gray-800">
                          🏆 {award.award_name} ({award.festival_name})
                        </Badge>
                      ))}
                  </div>
                </div>
                <div
                  className="grid"
                  style={{
                    gap: "12px",
                  }}
                >
                  <div
                    className="rounded-md font-bold"
                    style={{
                      backgroundColor: "rgba(63, 63, 70, 0.4)",
                      padding: "4px 8px",
                    }}
                  >
                    Nominations
                  </div>
                  <div>
                    <Accordion type="single" collapsible className="w-full">
                      {Object.entries(
                        groupByCriteria(
                          filmData.awards.filter(
                            (award: any) => !award.is_winner
                          ),
                          "festival_name"
                        )
                      ).map(([festival_name, awards]: any[], index: number) => (
                        <AccordionItem value={`item-${index}`} key={index}>
                          <AccordionTrigger>
                            <div className="flex gap-2">
                              <Badge className="bg-indigo-700">
                                ⭐️ {festival_name}
                              </Badge>
                              <p>{awards.length} nominations</p>
                            </div>
                          </AccordionTrigger>
                          <AccordionContent>
                            <div className="flex flex-wrap gap-2">
                              {awards.map((award: any, index: number) => (
                                <Badge className="bg-gray-800" key={index}>
                                  {award.award_name}
                                </Badge>
                              ))}
                            </div>
                          </AccordionContent>
                        </AccordionItem>
                      ))}
                    </Accordion>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}

// Note: Dans Next.js 13+ avec le répertoire app :
// - Les fichiers nommés page.tsx dans un dossier deviennent automatiquement des routes
// - Le dossier [slug] crée un segment de route dynamique
// - Le paramètre sera accessible via le hook useParams()
