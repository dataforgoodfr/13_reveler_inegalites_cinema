"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Menubar, MenubarMenu, MenubarTrigger } from "@/components/ui/menubar";
import Image from "next/image";
import { useParams } from "next/navigation";
import filmData from "./film.json";
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

  // État pour gérer la section active
  const [activeSection, setActiveSection] = useState("Statistiques");

  return (
    <main className="p-20 bg-transparent text-white">
      <div
        className="background-image"
        style={
          {
            "--background-image-url": `url(${filmData.image})`,
          } as React.CSSProperties
        }
      ></div>
      <div className="flex flex-col items-center md:flex-row gap-10">
        <div className="relative p-3">
          <Image
            style={{ height: "fit-content" }}
            src={filmData.image}
            alt="Affiche"
            height={342.5}
            width={257.45}
          />
          <div className="absolute flex flex-col gap-2">
          <Button variant="outline" size="icon" style={{
                opacity: 0.8,
              }}>
            <Image
              src="/video_search.svg"
              alt="Rechercher"
              width={24}
              height={24}
            />
          </Button>
          <Button variant="outline" size="icon" style={{
                opacity: 0.8,
              }}>
            <Image
              src="/frame_search.svg"
              alt="Rechercher"
              width={24}
              height={24}
            />
          </Button>
          <Button variant="outline" size="icon" style={{
                opacity: 0.8,
              }}>
            <Image
              src="/share.svg"
              alt="Rechercher"
              width={24}
              height={24}
            />
          </Button>
          </div>
        </div>
        <div className="w-full flex md:block flex-col">
          <h1 className="text-4xl font-bold mb-4">
            {filmData.title} ({filmData.year})
          </h1>
          <h2>Réalisé par {filmData.director}</h2>
          <p className="text-lg mb-2">
            {filmData.country} {filmData.airing_date} en salle{" "}
            {filmData.duration}
          </p>
          <div className="flex mb-4 gap-2">
            {filmData.tags.map((tag, index) => (
              <Badge key={index} className="bg-zinc-700">
                {tag}
              </Badge>
            ))}
          </div>
          <Dialog>
            {filmData.parity ? (
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
                        {Math.round(filmData.statistics.chiefs * 100)}%
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
                        {Math.round(filmData.statistics.main_casting * 100)}%
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
                <p>Distribué par</p>
                <Badge>{filmData.distribution.distributor}</Badge>
                <p className="mt-4">Produit par</p>
                <div className="flex flex-wrap mb-4">
                  {filmData.distribution.production.map((producer, index) => (
                    <Badge key={index}>{producer}</Badge>
                  ))}
                </div>
                <p>Budget</p>
                <p>{filmData.distribution.budget}</p>
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
                {filmData.film_crew.map((crew) => (
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
                      {crew.role}
                    </div>
                    <div>
                      {crew.members.map((member) => (
                        <Badge
                          className={
                            member.isMale ? "bg-slate-700" : "bg-violet-800"
                          }
                        >
                          {member.name}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeSection === "Casting" && (
              <div className="pt-5 flex flex-wrap gap-2">
                {filmData.casting.map((actor, index) => (
                  <Badge
                    key={index}
                    className={actor.isMale ? "bg-slate-700" : "bg-violet-800"}
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
                    {filmData.ranking.awards.map((award, index) => (
                      <Badge key={index} className="bg-gray-800">
                        ️ 🏆{award}
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
                    Sélections
                  </div>
                  <div>
                    <Accordion type="single" collapsible className="w-full">
                      {filmData.ranking.selections.map((selection, index) => (
                        <AccordionItem value={`item-${index}`} key={index}>
                          <AccordionTrigger>
                            <div className="flex gap-2">
                              <Badge className="bg-indigo-700">
                                ⭐️ {selection.name}
                              </Badge>
                              <p>{selection.nominations.length} nominations</p>
                            </div>
                          </AccordionTrigger>
                          <AccordionContent>
                            <div className="flex gap-2">
                              {selection.nominations.map(
                                (nomination, index) => (
                                  <Badge key={index} className="bg-gray-800">
                                    {nomination}
                                  </Badge>
                                )
                              )}
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
