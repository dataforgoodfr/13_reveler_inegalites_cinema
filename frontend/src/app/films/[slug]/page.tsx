"use client";

import { useEffect, useState } from "react";
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
        setFilmData(value);
        setIsLoading(false);
      })
      .catch(() => {
        setHasError(true);
        setIsLoading(false);
      });
  }, [slug]);

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
            "--background-image-url": `url(${filmData.film.poster_image_base64})`,
          } as React.CSSProperties
        }
      ></div>
      <div className="flex flex-col items-center md:items-start md:flex-row gap-10">
        <div className="relative -z-1">
          <img
            style={{ height: "fit-content" }}
            src={filmData.film.poster_image_base64}
            alt="Affiche"
            height={342.5}
            width={257.45}
          />
          <div className="absolute flex flex-col gap-2 bottom-2 left-2">
            <Button variant="outline" size="icon" style={{ opacity: 0.8 }}>
              <img
                src="/video_search.svg"
                alt="Rechercher"
                width={24}
                height={24}
              />
            </Button>
            <Button variant="outline" size="icon" style={{ opacity: 0.8 }}>
              <img
                src="/frame_search.svg"
                alt="Rechercher"
                width={24}
                height={24}
              />
            </Button>
            <Button variant="outline" size="icon" style={{ opacity: 0.8 }}>
              <img src="/share.svg" alt="Rechercher" width={24} height={24} />
            </Button>
          </div>
        </div>
        <div className="w-full flex md:block flex-col">
          <h1 className="text-4xl font-bold mb-4">
            {filmData.film.original_name} ({new Date(filmData.film.release_date).getFullYear()})
          </h1>
          <h2>Réalisé par {filmData.film.credits.find((c: any) => c.role === "director")?.name}</h2>
          <p className="text-lg mb-2">
            {filmData.film.top_budget_country} {filmData.film.release_date} en salle{" "}
            {filmData.film.budget.toLocaleString()} €
          </p>
          <div className="flex mb-4 gap-2">
            {filmData.film.genres.map((genre: string, index: number) => (
              <Badge key={index} className="bg-zinc-700">
                {genre}
              </Badge>
            ))}
          </div>
          <Dialog>
            {filmData.film.parity_bonus ? (
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
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Bonus parité du CNC</DialogTitle>
                <DialogDescription>
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
                  <Card
                    className="md:w-[220px]"
                    style={{
                      borderColor: "rgba(51, 51, 51, 1)",
                      backgroundColor: "rgba(30, 30, 30, 0.8)",
                    }}
                  >
                    <CardHeader>
                      <CardTitle className="text-violet-300">
                        {filmData.film.female_representation_in_key_roles}%
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
                        {filmData.film.female_representation_in_casting}%
                      </CardTitle>
                      <CardDescription className="text-white">
                        de femmes dans{" "}
                        <span className="text-violet-300">
                          le casting principal
                        </span>
                      </CardDescription>
                    </CardHeader>
                  </Card>
                </div>
              </div>
            )}

            {activeSection === "Distribution" && (
              <div className="mt-4">
                <h2 className="text-2xl font-bold mb-4">Distribution</h2>
                <p>Budget</p>
                <p>{filmData.film.budget.toLocaleString()} €</p>
              </div>
            )}

            {activeSection === "Equipe du film" && (
              <div
                className="mt-4 grid grid-cols-2"
                style={{
                  columnGap: "80px",
                  rowGap: "24px",
                }}
              >
                {filmData.film.credits.map((credit: any, index: number) => (
                  <div
                    key={index}
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
                      {credit.role}
                    </div>
                    <div>
                      <Badge
                        className={
                          credit.gender === "male"
                            ? "bg-slate-700"
                            : "bg-violet-800"
                        }
                      >
                        {credit.name}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeSection === "Casting" && (
              <div className="pt-5 flex flex-wrap gap-2">
                {filmData.film.credits
                  .filter((credit: any) => credit.role === "actor")
                  .map((actor: any, index: number) => (
                    <Badge
                      key={index}
                      className={
                        actor.gender === "male" ? "bg-slate-700" : "bg-violet-800"
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
                  <div>
                    {filmData.film.awards
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
                      {filmData.film.awards
                        .filter((award: any) => !award.is_winner)
                        .map((nomination: any, index: number) => (
                          <AccordionItem value={`item-${index}`} key={index}>
                            <AccordionTrigger>
                              <div className="flex gap-2">
                                <Badge className="bg-indigo-700">
                                  ⭐️ {nomination.award_name}
                                </Badge>
                                <p>{nomination.festival_name}</p>
                              </div>
                            </AccordionTrigger>
                            <AccordionContent>
                              <div className="flex gap-2">
                                <Badge className="bg-gray-800">
                                  {nomination.date}
                                </Badge>
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
