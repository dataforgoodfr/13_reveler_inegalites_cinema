"use client";

import { Ref, useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { ChevronUp, Mouse } from "lucide-react";

export default function PageAbout() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [activeId, setActiveId] = useState('');
  const observer: Ref<IntersectionObserver> = useRef(null);
  const sections = [
  { id: 'section-1', label: 'Notre mission' },
  { id: 'section-2', label: 'Les chiffres clés' },
  { id: 'section-3', label: "Comment fonctionne l'Observatoire ?" }
];

  useEffect(() => {
    const handleIntersect: IntersectionObserverCallback = (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          setActiveId(entry.target.id);
        }
      });
    };

    observer.current = new IntersectionObserver(handleIntersect, {
      rootMargin: '0px 0px -60% 0px',
      threshold: 0.1,
    });

    sections.forEach(({ id }) => {
      const el = document.getElementById(id);
      if (el && observer.current) observer.current.observe(el);
    });

    return () => {
      if (observer.current) observer.current.disconnect();
    };
  }, []);

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
      <main
        className="container mx-auto px-10 py-16 flex flex-col items-center justify-center text-white"
        style={{ background: 'unset' }}
      >
        <div
          id="section-top"
          className="w-full flex items-center justify-center"
          style={{ height: "calc(100vh - var(--spacing)* 16)" }}
        >
          <div className="w-[897px] h-[379px] flex flex-col justify-around">
            <h1 className="text-4xl text-center font-bold">
             L&apos;Observatoire des inégalités dans l&apos;industrie du cinéma,{" "}
             <span className="text-violet-300">c&apos;est quoi ?</span>
            </h1>
            <div className="flex justify-center">
              <div className="flex flex-col items-center">
                <span>Défilez pour découvrir</span>
                <Button
                  className="bg-transparent hover:bg-transparent text-white"
                  size={"icon"}
                  onClick={() => scrollToSection("section-below")}
                >
                  <Mouse />
                </Button>
              </div>
            </div>
          </div>
        </div>
        <div id="section-below" className="py-16 flex">
          <nav className="hidden md:block w-64 sticky top-0 p-3 text-white h-fit">
            <ul className="space-y-4 border-l-2">
              {sections.map(({ id, label }) => (
                <li key={id}>
                  <a
                    href={`#${id}`}
                    className={`block pl-2 transition-colors ${
                      activeId === id ? 'text-[#A984FF] font-bold border-l-4 border-[#A984FF]' : 'text-white'
                    }`}
                  >
                    {label}
                  </a>
                </li>
              ))}
            </ul>
          </nav>
          <div className="flex flex-col gap-10">            
            <section id="section-1" className="flex flex-col gap-5 scroll-mt-32">
              <h1 className="text-2xl text-violet-300 font-bold">
                Mesurer pour agir : une boîte à outils au service d&apos;un cinéma plus
                inclusif
              </h1>
              <div className="flex flex-col gap-5">
                <span>
                Le cinéma et l&apos;audiovisuel façonnent nos imaginaires collectifs,
                mais <span className="font-bold">reflètent-ils vraiment la diversité de notre société ?</span>
                </span>
                <span>
                Derrière la caméra comme à l&apos;écran, <span className="font-bold">les inégalités persistent</span> :
                manque de représentation, faible visibilité des femmes et des
                minorités…  
                </span>
                <span>
                Pour objectiver ces réalités et impulser un changement
                concret, nous avons créé <span className="font-bold">une boîte à outils data-driven</span>. Cet
                observatoire analyse, mesure et met en lumière les déséquilibres
                dans l&apos;industrie du cinéma grâce à des données précises et
                accessibles.
                </span>
              </div>
            </section>
            <section id="section-2" className="flex flex-col gap-5 scroll-mt-32">
              <h1 className="text-2xl text-violet-300 font-bold">
                Les chiffres clés
              </h1>
              <span>
                Malgré une prise de conscience grandissante, ces chiffres montrent
                à quel point la représentation est encore{" "}
                <span className="font-bold">inégale</span>.
              </span>
              <div className="flex p-5 flex-col gap-5">
                <div className="flex w-full items-center">
                  <span className="text-4xl pr-2 font-bold text-violet-300">
                    1/4
                  </span>
                  <span className="text-white">
                    de films réalisés par des <span className="text-violet-300 font-bold">femmes</span>{" "}
                    ces 10 dernières années
                  </span>
                </div>
                <div className="flex w-full items-center">
                  <span className="text-4xl pr-2 font-bold text-violet-300">
                    37%
                  </span>
                  <span className="text-white">
                    de budget <span className="text-violet-300 font-bold">en moins</span>{" "}
                    pour les réalisatrices ces 10 dernières années 
                  </span>
                </div>
                <div className="flex w-full items-center">
                  <span className="text-4xl pr-2 font-bold text-violet-300">
                    10%
                  </span>
                  <span className="text-white">
                    des récompenses ont été attribuées à des <span className="text-violet-300 font-bold">réalisatrices</span>{" "}
                    à Cannes, Berlin et Venise
                  </span>
                </div>
              </div>
            </section>
            <section id="section-3" className="flex flex-col gap-5 scroll-mt-32">
              <h1 className="text-2xl text-violet-300 font-bold">
                Ce que permet l&apos;Observatoire
              </h1>
              <div>
                <h2 className="text-violet-300 font-bold">
                  Rechercher par film
                </h2>
                <span>
                  Informez-vous sur le degré d&apos;inclusion dans la constitution des équipes techniques et artistiques
                </span>
              </div>
              <div>
                <h2 className="text-violet-300 font-bold">
                  Analyser les données
                </h2>
                <span>
                  Vous pouvez croiser des données en utilisant plusieurs filtres : budget, genre cinématographique, diffuseur, chef·fe de poste, etc.
                </span>
              </div>
              <div>
                <h2 className="text-violet-300 font-bold">
                  Visualiser les tendances
                </h2>
                <span>
                  La base de données permet d&apos;analyser l&apos;évolution des inégalités sur 20 ans
                </span>
              </div>
            </section>
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
