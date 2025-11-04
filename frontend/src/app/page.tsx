import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function Home() {
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
        className="container h-full mx-auto px-4 py-16 flex flex-col items-center justify-center text-center text-white"
        style={{ background: 'unset' }}
      >
        <div className="animate-slide-up flex flex-col items-center gap-8">
          <div>
            <span className="text-5xl md:text-6xl font-bold w-3/4">
              <span>Seules{" "}</span>
              <span className="text-violet-500">29%</span>
              <span>
                {" "}
                des cinéastes{" "}
                <br className="hidden md:block" />
                ces dix dernières années sont des{" "}
              </span>
              <span className="text-violet-500">femmes</span>
            </span>
          </div>
          <Button className="bg-violet-500 cursor-pointer">
            Rechercher par film
          </Button>
          <Link href="/statistics">
            <Button className="bg-violet-500 cursor-pointer">
              Voir les statistiques globales
            </Button>
          </Link>
          <span>Outil d&apos;analyse conçu par le Collectif 5050 et Data4 Good</span>
        </div>
      </main>
    </>
  );
}
