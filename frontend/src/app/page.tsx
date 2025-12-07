"use client";

import { Button } from "@/components/ui/button";
import Link from "next/link";
import { useSearchContext } from "@/contexts/SearchContext";

export default function Home() {
  const { openSearch } = useSearchContext();
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
        className="container h-full mx-auto px-4 pt-64 md:pt-96 flex flex-col items-center justify-center text-center text-white"
        style={{ background: "unset" }}
      >
        <div className="animate-slide-up flex flex-col items-center gap-8">
          <p className="text-5xl md:text-6xl text-shadow-sm text-shadow-black font-bold md:w-5/6 leading-tight">
            Seules <span className="text-violet-500">29%</span> des cinéastes de
            ces dix dernières années sont des{" "}
            <span className="text-violet-500">femmes</span>
          </p>
          <Button className="bg-violet-500 cursor-pointer" onClick={openSearch}>
            Rechercher par film
          </Button>
          <Link href="/statistics">
            <Button className="bg-violet-500 cursor-pointer">
              Voir les statistiques globales
            </Button>
          </Link>
          <span>
            Outil d&apos;analyse conçu par le Collectif 50/50 et Data For Good
          </span>
        </div>
      </main>
    </>
  );
}
