"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Menubar, MenubarMenu, MenubarTrigger } from "@/components/ui/menubar";
import { useParams } from "next/navigation";
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
import { Film } from "@/dto/film/film.dto";
import { FilmApiResponse } from "@/dto/film/film-api-response.dto";
import { Award } from "@/dto/film/award.dto";
import { Credit } from "@/dto/film/credit.dto";
import Link from "next/link";
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";
import { API_URL } from "@/utils/api-url";
import { nameToUpperCase } from "@/utils/name-to-uppercase";
import CncDialog from "@/components/atoms/CncDialog";
import FrameSearch from "@/icons/frame_search";
import VideoSearch from "@/icons/video_search";
import Share from "@/icons/share";
import { Distribution } from "@/dto/film/distribution.dto";

// Ceci est un composant de page avec une route dynamique
// Le [slug] dans le nom du dossier sera disponible comme paramètre
export default function PageFilm() {
  // useParams est un hook qui permet d'accéder aux paramètres dynamiques de l'URL
  const params = useParams();
  const slug = params?.slug as string; // Ajout du typage explicite
  const [filmData, setFilmData] = useState<Film | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [activeSection, setActiveSection] = useState("Statistiques");
  const [openDrawer, setOpenDrawer] = useState(false);
  const [openTrailerDialog, setOpenTrailerDialog] = useState(false);
  const [openShareDialog, setOpenShareDialog] = useState(false);
  const [openPosterDialog, setOpenPosterDialog] = useState(false);
  const [openCncDialog, setOpenCncDialog] = useState(false);

  useEffect(() => {
    const url = `${API_URL}/films/${slug}`;

    fetch(url)
      .then((response) => {
        if (response.ok) {
          return response.json();
        }
        throw new Error("Fetch error");
      })
      .then((value: FilmApiResponse) => {
        setFilmData(value.film);
        setIsLoading(false);
      })
      .catch(() => {
        setHasError(true);
        setIsLoading(false);
      });
  }, [slug]);

  const getDate = (dateStr: string) => {
    const date = new Date(dateStr);

    const options: Intl.DateTimeFormatOptions = {
      day: "numeric",
      month: "long",
      year: "numeric",
    };
    return new Intl.DateTimeFormat("fr-FR", options).format(date);
  };

  const groupByCriteria = <T, K extends keyof T>(
    list: T[],
    criteria: K
  ): Record<string, T[]> => {
    return list.reduce((acc: Record<string, T[]>, element: T) => {
      const data = element[criteria] as string;

      if (!acc[data]) {
        acc[data] = [];
      }

      acc[data].push(element);
      return acc;
    }, {});
  };

  const getDistribution = (
    distribution: Distribution
  ): Record<string, Credit[]> => {
    return {
      distribution: distribution.distribution,
      production: distribution.production,
      'co-production': distribution["co-production"],
      financiers: distribution.financiers,
    };
  };

  const getBackgroundColorFromGender = (gender?: string) => {
    switch (gender) {
      case "male":
        return "bg-slate-700";
      case "female":
        return "bg-violet-800";
      default:
        return "bg-[#525252]";
    }
  };

  if (isLoading || !filmData) {
    return (
      <main className="p-20 min-h-screen h-full bg-transparent text-white flex justify-center items-center">
        <p>Chargement...</p>
      </main>
    );
  }

  if (hasError) {
    return (
      <main className="p-20 min-h-screen h-full bg-transparent text-white flex justify-center items-center">
        <h1 className="text-4xl font-bold">404 - Film non trouvé</h1>
      </main>
    );
  }

  return (
    <main className="p-10 md:p-20 min-h-screen text-white">
      <div className="flex flex-col items-center md:items-start md:flex-row gap-10">
        <div className="pt-5 md:pt-0 flex flex-col gap-4">
          <div className="relative shadow-[0_0_40px_rgba(255,255,255,0.2)] rounded-md">
            {filmData.poster_image_base64 &&
            filmData.poster_image_base64 !== "" ? (
              <Image
                loader={({ src }) => src}
                className="rounded-md"
                style={{ height: "fit-content" }}
                src={filmData.poster_image_base64}
                alt="Affiche"
                width={257.45}
                height={0}
              />
            ) : (
              <Image
                className="rounded-md"
                style={{ height: "fit-content" }}
                src="/placeholder_image.svg"
                alt="Image indisponible"
                width={257.45}
                height={0}
              />
            )}
            <div className="flex absolute md:hidden flex-col gap-2 bottom-2 right-2 text-black">
              <Drawer open={openDrawer} onOpenChange={setOpenDrawer}>
                <DrawerTrigger asChild>
                  <Button variant="outline" size="icon" style={{ opacity: 0.8 }}>
                    ...
                  </Button>
                </DrawerTrigger>
                {openDrawer && (
                  <DrawerContent className="bg-[#1D1F20] text-white">
                    <DrawerTitle />
                    <DrawerDescription />
                    <div className="p-10 flex flex-col gap-10">
                      <div
                        className="flex items-center gap-5"
                        onClick={() => {
                          setOpenPosterDialog(true);
                          setOpenDrawer(false);
                        }}
                      >
                        <FrameSearch size={30}/>
                        <span className="text-xl">Analyser l&apos;affiche du film</span>
                      </div>
                      <div
                        className="flex items-center gap-5"
                        onClick={() => {
                          setOpenTrailerDialog(true);
                          setOpenDrawer(false);
                        }}
                      >
                        <VideoSearch size={30}/>
                        <span className="text-xl">Analyser la bande-annonce</span>
                      </div>
                      <div
                        className="flex items-center gap-5"
                        onClick={() => {
                          setOpenShareDialog(true);
                          setOpenDrawer(false);
                        }}
                      >
                        <Share size={30}/>
                        <span className="text-xl">Partager la fiche du film</span>
                      </div>
                    </div>
                  </DrawerContent>
                )}
              </Drawer>
            </div>
          </div>
          <PosterAnalysisDialog
            open={openPosterDialog}
            setOpen={setOpenPosterDialog}
            imageSource={filmData.poster_image_base64}
            femaleVisibleRatioOnPoster={
              filmData.metrics?.female_visible_ratio_on_poster
            }
            nonWhiteVisibleRatioOnPoster={
              filmData.metrics?.non_white_visible_ratio_on_poster
            }
          />
          <TrailerAnalysisDialog
            open={openTrailerDialog}
            setOpen={setOpenTrailerDialog}
            filmName={filmData.original_name}
            releaseDate={filmData.release_date}
            trailerUrl={filmData.trailer_url ?? ""}
            femaleScreenTimeInTrailer={
              filmData.metrics?.female_screen_time_in_trailer
            }
            nonWhiteScreenTimeInTrailer={
              filmData.metrics?.non_white_screen_time_in_trailer
            }
          />
          <ShareDialog
            open={openShareDialog}
            setOpen={setOpenShareDialog}
            imageSource={filmData.poster_image_base64}
          />
          <div className="hidden md:flex flex-col gap-2 left-2">
            <Button
              className="w-full bg-zinc-700 justify-start"
              style={{ opacity: 0.8 }}
              onClick={() => setOpenPosterDialog(true)}
            >
              <FrameSearch size={24} color="white" />
              Analyser l&apos;affiche du film
            </Button>
            <Button
              className="w-full bg-zinc-700 justify-start"
              style={{ opacity: 0.8 }}
              onClick={() => setOpenTrailerDialog(true)}
            >
              <VideoSearch size={24} color="white" />
              Analyser la bande annonce
            </Button>
            <Button
              className="w-full bg-zinc-700 justify-start"
              style={{ opacity: 0.8 }}
              onClick={() => setOpenShareDialog(true)}
            >
              <Share size={24} color="white" />
              <p>Partager le film</p>
            </Button>
          </div>
        </div>
        <div className="w-full flex md:block flex-col">
          <h1 className="text-4xl font-bold mb-4">
            {filmData.original_name + " "}
            <span className="text-sm">
              (
              {filmData.release_date
                ? new Date(filmData.release_date).getFullYear()
                : "NC"}
              )
            </span>
          </h1>
          <div className="flex flex-col gap-2">
            <div className="flex flex-col">
              <span className="text-sm text-[#CBD5E1]">
                Réalisé par
              </span>
              <span className="font-bold">
                {filmData.credits?.key_roles
                  ? filmData.credits.key_roles
                      .filter((c: Credit) => c.role === "director")
                      .map((c: Credit) => !c.name ? '' : c.name.split(' ').map(nameToUpperCase).join(' '))
                      .join(", ")
                  : "NC"}
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-sm text-[#CBD5E1]">
                Sortie le
              </span>
              <span className="font-bold">
                {filmData.release_date
                  ? `${getDate(filmData.release_date)} en salle`
                  : "Date inconnue"}
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-sm text-[#CBD5E1]">
                Durée
              </span>
              <span className="font-bold">
                {filmData.duration || "Durée inconnue"}
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-sm text-[#CBD5E1]">
                Pays de production
              </span>
              <span className="font-bold">
                {filmData.countries_sorted_by_budget?.length
                  ? filmData.countries_sorted_by_budget.join(", ")
                  : "NC"}
              </span>
            </div>
            <div className="flex mb-4 gap-2">
              {filmData.genres?.length ? (
                filmData.genres.map((genre: string, index: number) => (
                  <Badge key={index} className="bg-zinc-700 rounded-full">
                    {genre}
                  </Badge>
                ))
              ) : (
                <span className="text-white">Genres non renseignés</span>
              )}
            </div>
            {filmData.parity_bonus ? (
                <Button className="bg-green-200 hover:bg-green-200 text-green-950 rounded-full w-fit">
                  Bonus parité du CNC
                  <div className="cursor-pointer" onClick={() => setOpenCncDialog(!openCncDialog)}>
                    <Image
                      src="/info.svg"
                      alt="Rechercher"
                      width={24}
                      height={24}
                    />
                  </div>
                </Button>
              ) : (
                <Button className="bg-red-200 hover:bg-red-200 text-red-950 rounded-full w-fit">
                  Film non éligible au bonus parité du CNC
                  <div className="cursor-pointer" onClick={() => setOpenCncDialog(!openCncDialog)}>
                    <Image
                      src="/info.svg"
                      alt="Rechercher"
                      width={24}
                      height={24}
                    />
                  </div>
                </Button>
              )}
          </div>
          <CncDialog open={openCncDialog} setOpen={setOpenCncDialog}/>
          <div className="mt-8">
            <Menubar className="w-full md:w-fit overflow-y-hidden">
              <MenubarMenu>
                <MenubarTrigger
                  className={activeSection === "Statistiques" ? 'bg-white text-black' : ''}
                  onClick={() => setActiveSection("Statistiques")}
                >
                  Statistiques
                </MenubarTrigger>
              </MenubarMenu>
              <MenubarMenu>
                <MenubarTrigger
                  className={activeSection === "Distribution" ? 'bg-white text-black' : ''}
                  onClick={() => setActiveSection("Distribution")}
                >
                  Financement
                </MenubarTrigger>
              </MenubarMenu>
              <MenubarMenu>
                <MenubarTrigger
                  className={"whitespace-nowrap" + activeSection === "Casting" ? ' bg-white text-black' : ''}
                  onClick={() => setActiveSection("Equipe du film")}
                >
                  Equipe du film
                </MenubarTrigger>
              </MenubarMenu>
              <MenubarMenu>
                <MenubarTrigger 
                  className={activeSection === "Casting" ? 'bg-white text-black' : ''}
                  onClick={() => setActiveSection("Casting")}
                >
                  Casting
                </MenubarTrigger>
              </MenubarMenu>
              <MenubarMenu>
                <MenubarTrigger
                  className={activeSection === "Palmarès" ? 'bg-white text-black' : ''}
                  onClick={() => setActiveSection("Palmarès")}
                >
                  Palmarès
                </MenubarTrigger>
              </MenubarMenu>
            </Menubar>

            {/* Affichage conditionnel des sections */}
            {activeSection === "Statistiques" && (
              <div className="mt-4">
                <div className="flex flex-col md:flex-row gap-5">
                  {filmData.metrics?.female_representation_in_key_roles ||
                  filmData.metrics?.female_representation_in_casting ? (
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
                            {filmData.metrics
                              ?.female_representation_in_key_roles
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
                            {filmData.metrics?.female_representation_in_casting
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

            {activeSection === "Distribution" &&
              (filmData.credits?.distribution ? (
                <>
                  <div className="mt-4">
                    <span
                      className="block rounded-sm font-bold w-full px-2 py-1"
                    >
                      Budget
                    </span>
                    <div className="px-2 py-1">
                      <span>
                        {filmData.credits.distribution.budget
                          ? filmData.credits.distribution.budget.toLocaleString() + " €"
                          : "NC"}
                      </span>
                    </div>
                  </div>
                  {Object.entries(getDistribution(filmData.credits.distribution))
                  .filter(
                    (
                      value: [string, Credit[]],
                    ) => value[1].length
                  )
                  .map(
                    (
                      [role, credits]: [string, Credit[]],
                      role_index: number
                    ) => (
                      <div key={role_index} className="mt-4">
                        <span
                          className="block rounded-sm font-bold w-full px-2 py-1"
                        >
                          {t(`distribution.${role}`)}
                        </span>
                        <div className="flex flex-wrap">
                          {credits.map((credit: Credit, index: number) => (
                            <div className="px-2 py-1" key={index}>
                              <span className="bg-gray-800 py-1 px-2 rounded-sm text-slate-300 text-sm">
                                {credit.name}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )
                  )}
                </>
              ) : (
                <div className="mt-4 text-white">
                  Aucune donnée de distribution disponible.
                </div>
              ))}

            {activeSection === "Equipe du film" &&
              (filmData.credits?.key_roles &&
              filmData.credits.key_roles.length > 0 ? (
                <div
                  className="mt-4 flex flex-col md:grid md:grid-cols-2"
                  style={{
                    columnGap: "80px",
                    rowGap: "24px",
                  }}
                >
                  {Object.entries(
                    groupByCriteria(filmData.credits.key_roles, "role")
                  ).map(
                    ([role_name, roles]: [string, Credit[]], index: number) => (
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
                          {roles.map((role: Credit, idx: number) => (
                            <Badge
                              key={idx}
                              className={
                                getBackgroundColorFromGender(role.gender)
                              }
                            >
                              {nameToUpperCase(role.name)}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )
                  )}
                </div>
              ) : (
                <div className="mt-4 text-white">
                  Aucune donnée d&apos;équipe disponible.
                </div>
              ))}

            {activeSection === "Casting" &&
              (filmData.credits?.casting &&
              filmData.credits.casting.length > 0 ? (
                <div className="pt-5 grid grid-cols-2 md:flex md:flex-wrap gap-2">
                  {filmData.credits.casting.map(
                    (actor: Credit, index: number) => (
                      <Badge
                        key={index}
                        className={
                          getBackgroundColorFromGender(actor.gender)
                        }
                      >
                        {nameToUpperCase(actor.name)}
                      </Badge>
                    )
                  )}
                </div>
              ) : (
                <div className="mt-4 text-white">
                  Aucune donnée de casting disponible.
                </div>
              ))}

            {activeSection === "Palmarès" &&
              (filmData.awards && filmData.awards.length > 0 ? (
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
                        .filter((award: Award) => award.is_winner)
                        .map((award: Award, index: number) => (
                          <Badge key={index} className="bg-gray-800">
                            <Link href={`/festivals/${award.festival_id}`}>
                              🏆 {award.award_name} ({award.festival_name})
                            </Link>
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
                              (award: Award) => !award.is_winner
                            ),
                            "festival_id"
                          )
                        ).map(
                          (
                            [festival_id, awards]: [string, Award[]],
                            index: number
                          ) => (
                            <AccordionItem value={`item-${index}`} key={index}>
                              <AccordionTrigger>
                                <div className="flex gap-2">
                                  <Link
                                    href={`/festivals/${festival_id}`}
                                    className="text-indigo-400 underline"
                                  >
                                    ⭐️ {awards[0].festival_name}
                                  </Link>
                                  <p>{awards.length} nominations</p>
                                </div>
                              </AccordionTrigger>
                              <AccordionContent>
                                <div className="flex flex-wrap gap-2">
                                  {awards.map((award: Award, index: number) => (
                                    <Badge className="bg-gray-800" key={index}>
                                      {award.award_name}
                                    </Badge>
                                  ))}
                                </div>
                              </AccordionContent>
                            </AccordionItem>
                          )
                        )}
                      </Accordion>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="mt-4 text-white">
                  Aucune donnée de palmarès disponible.
                </div>
              ))}
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
