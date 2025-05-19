"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ChevronDown, ChevronUp } from "lucide-react";

export default function PageAbout() {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 0);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToSection = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
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
      <main className="container mx-auto px-10 py-16 flex flex-col items-center justify-center text-white">
        <div
          id="section-top"
          className="w-full flex items-center justify-center"
          style={{ height: "calc(100vh - var(--spacing)* 16)" }}
        >
          <div className="w-[897px] h-[379px] flex flex-col justify-around">
            <span className="block w-full text-violet-300 underline">
              A PROPOS
            </span>
            <h1 className="text-4xl text-center font-bold">
              L’Observatoire de l’inclusion et de l’équité dans l’industrie du
              cinéma, <span className="text-violet-300">c’est quoi ?</span>
            </h1>
            <div className="flex justify-center">
              <div className="flex gap-5 items-center">
                <Button
                  className="rounded-full bg-violet-300 hover:bg-violet-300 text-black"
                  size={"icon"}
                  onClick={() => scrollToSection("section-below")}
                >
                  <ChevronDown />
                </Button>
                <span>Défilez pour découvrir</span>
              </div>
            </div>
          </div>
        </div>
        <div id="section-below" className="py-16 flex flex-col gap-10">
          <div className="flex flex-col gap-5">
            <h1 className="text-2xl text-violet-300 font-bold">
              Mesurer pour agir : une boîte à outils au service d’un cinéma plus
              inclusif
            </h1>
            <div className="flex flex-col gap-5">
              <span>
              Le cinéma et l’audiovisuel façonnent nos imaginaires collectifs,
              mais <span className="text-violet-300 font-bold">reflètent-ils vraiment la diversité de notre société ?</span>
              </span>
              <span>
              Derrière la caméra comme à l’écran, <span className="text-violet-300 font-bold">les inégalités persistent</span> :
              manque de représentation, faible visibilité des femmes et des
              minorités…  
              </span>
              <span>
              Pour objectiver ces réalités et impulser un changement
              concret, nous avons créé <span className="text-violet-300 font-bold">une boîte à outils data-driven</span>. Cet
              observatoire analyse, mesure et met en lumière les déséquilibres
              dans l’industrie du cinéma grâce à des données précises et
              accessibles.
              </span>
            </div>
          </div>
          <div className="flex flex-col gap-5">
            <h1 className="text-2xl text-violet-300 font-bold">
              Les chiffres clés
            </h1>
            <div className="flex gap-10">
              <Card className="w-full bg-[#282828] border-[#051525]">
                <CardHeader>
                  <CardTitle className="text-4xl text-violet-300">
                    23%
                  </CardTitle>
                  <CardDescription className="text-white">
                    films réalises par des femmes en 2024
                  </CardDescription>
                </CardHeader>
              </Card>
              <Card className="w-full bg-[#282828] border-[#051525]">
                <CardHeader>
                  <CardTitle className="text-4xl text-violet-300">
                    25%
                  </CardTitle>
                  <CardDescription className="text-white">
                    de budget <span className="text-violet-300">en moins</span>{" "}
                    pour les réalisatrices
                  </CardDescription>
                </CardHeader>
              </Card>
              <Card className="w-full bg-[#282828] border-[#051525]">
                <CardHeader>
                  <CardTitle className="text-4xl text-violet-300">
                    25%
                  </CardTitle>
                  <CardDescription className="text-white">
                    de budget <span className="text-violet-300">en moins</span>{" "}
                    pour les réalisatrices
                  </CardDescription>
                </CardHeader>
              </Card>
            </div>
            <span>
              Malgré une prise de conscience grandissante, ces chiffres montrent
              à quel point la représentation est encore{" "}
              <span className="text-violet-300">inégale</span>.
            </span>
          </div>
          <div className="flex flex-col gap-5">
            <h1 className="text-2xl text-violet-300 font-bold">
              Comment fonctionne l’Observatoire ?
            </h1>
            <div>
              <h2 className="text-violet-300 font-bold">
                Recherchez un film ou un festival
              </h2>
              <span>
                Lorem ipsum dolor sit amet consectetur. Turpis malesuada
                imperdie pharetra ac interdum mauris egestas elit cras. Odio at
                at congue aliquet.
              </span>
            </div>
            <div>
              <h2 className="text-violet-300 font-bold">
                Analysez les données
              </h2>
              <span>
                Lorem ipsum dolor sit amet consectetur. Turpis malesuada
                imperdie pharetra ac interdum mauris egestas elit cras. Odio at
                at congue aliquet.
              </span>
            </div>
            <div>
              <h2 className="text-violet-300 font-bold">
                Visualisez les tendances
              </h2>
              <span>
                Lorem ipsum dolor sit amet consectetur. Turpis malesuada
                imperdie pharetra ac interdum mauris egestas elit cras. Odio at
                at congue aliquet.
              </span>
            </div>
          </div>
        </div>
        {isScrolled && (
          <Button
            size={"icon"}
            className="fixed right-5 bottom-5 rounded-full bg-violet-300 hover:bg-violet-300 text-black"
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          >
            <ChevronUp />
          </Button>
        )}
      </main>
    </>
  );
}
