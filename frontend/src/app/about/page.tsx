"use client";

import { useRef } from "react";
import { Button } from "@/components/ui/button";
import { Mouse } from "lucide-react";

export default function PageAbout() {
  const sectionBelowRef = useRef<HTMLDivElement | null>(null);

  const scrollToSectionBelow = () => {
    sectionBelowRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <>
      <div
        className="background-image"
        style={
          {
            "--background-image-url": `url('/home.jpg')`,
          } as React.CSSProperties
        }
      ></div>
      <main
        className="container mx-auto px-10 py-16 flex flex-col items-center justify-center text-white"
        style={{ background: "unset" }}
      >
        <div
          className="w-full flex items-center justify-center"
          style={{ height: "calc(100vh - var(--spacing) * 16)" }}
        >
          <div className="flex pt-96 flex-col">
            <h1 className="text-5xl mb-8 text-center font-bold text-shadow-sm text-shadow-black">
              CinéStats 50/50,{" "}
              <span className="text-violet-300">c&apos;est quoi ?</span>
            </h1>
            <div className="flex justify-center">
              <div className="flex flex-col items-center">
                <span>Défilez pour découvrir</span>
                <Button
                  className="bg-transparent hover:bg-transparent text-white"
                  size={"icon"}
                  onClick={scrollToSectionBelow}
                >
                  <Mouse />
                </Button>
              </div>
            </div>
          </div>
        </div>
        <div ref={sectionBelowRef} className="py-16 w-full flex justify-center">
          <div className="flex flex-col gap-10">
            <section className="flex flex-col gap-5">
              <h1 className="text-2xl text-violet-300 font-bold">
                Mesurer pour agir : une boîte à outils au service d&apos;un
                cinéma plus inclusif
              </h1>
              <div className="flex flex-col gap-5">
                <span>
                  Le cinéma et l&apos;audiovisuel façonnent nos imaginaires
                  collectifs, mais{" "}
                  <span className="font-bold">
                    reflètent-ils vraiment la diversité de notre société ?
                  </span>
                </span>
                <span>
                  Derrière la caméra comme à l&apos;écran,{" "}
                  <span className="font-bold">les inégalités persistent</span> :
                  manque de représentation, faible visibilité des femmes et des
                  minorités…
                </span>
                <span>
                  Pour objectiver ces réalités et impulser un changement
                  concret, nous avons créé{" "}
                  <span className="font-bold">
                    une boîte à outils data-driven
                  </span>
                  . Cet observatoire analyse, mesure et met en lumière les
                  déséquilibres dans l&apos;industrie du cinéma grâce à des
                  données précises et accessibles.
                </span>
              </div>
            </section>
            <section className="flex flex-col gap-5">
              <h1 className="text-2xl text-violet-300 font-bold">
                Les chiffres clés
              </h1>
              <span>
                Malgré une prise de conscience grandissante, ces chiffres
                montrent à quel point la représentation est encore{" "}
                <span className="font-bold">inégale</span>.
              </span>
              <div className="flex p-5 flex-col gap-5">
                <div className="flex w-full items-center">
                  <span className="text-4xl pr-2 font-bold text-violet-300">
                    1/4
                  </span>
                  <span className="text-white">
                    de films réalisés par des{" "}
                    <span className="text-violet-300 font-bold">femmes</span>{" "}
                    ces 10 dernières années
                  </span>
                </div>
                <div className="flex w-full items-center">
                  <span className="text-4xl pr-2 font-bold text-violet-300">
                    37%
                  </span>
                  <span className="text-white">
                    de budget{" "}
                    <span className="text-violet-300 font-bold">en moins</span>{" "}
                    pour les réalisatrices ces 10 dernières années
                  </span>
                </div>
                <div className="flex w-full items-center">
                  <span className="text-4xl pr-2 font-bold text-violet-300">
                    10%
                  </span>
                  <span className="text-white">
                    des récompenses ont été attribuées à des{" "}
                    <span className="text-violet-300 font-bold">
                      réalisatrices
                    </span>{" "}
                    à Cannes, Berlin et Venise
                  </span>
                </div>
              </div>
            </section>
            <section className="flex flex-col gap-5">
              <h1 className="text-2xl text-violet-300 font-bold">
                Ce que permet CinéStats 50/50
              </h1>
              <div>
                <h2 className="text-violet-300 font-bold">
                  Rechercher par film
                </h2>
                <span>
                  Informez-vous sur le degré d&apos;inclusion dans la
                  constitution des équipes techniques et artistiques
                </span>
              </div>
              <div>
                <h2 className="text-violet-300 font-bold">
                  Analyser les données
                </h2>
                <span>
                  Vous pouvez croiser des données en utilisant plusieurs filtres
                  : budget, genre cinématographique, diffuseur, chef·fe de
                  poste, etc.
                </span>
              </div>
              <div>
                <h2 className="text-violet-300 font-bold">
                  Visualiser les tendances
                </h2>
                <span>
                  La base de données permet d&apos;analyser l&apos;évolution des
                  inégalités sur 20 ans
                </span>
              </div>
            </section>
          </div>
        </div>
        <p className="text-sm text-white/80 text-center">
          Photo d’illustration : © Lilies Films – ARTE France
        </p>
      </main>
    </>
  );
}
