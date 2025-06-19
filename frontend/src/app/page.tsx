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
      <main className="container h-full mx-auto px-4 py-16 flex flex-col items-center justify-center text-center text-white">
        <div className="animate-slide-up flex flex-col items-center gap-8">
          <div>
            <span className="text-5xl md:text-6xl font-bold w-3/4">
              <span className="text-violet-500">29%</span>
              <span>
                {" "}
                des réalisateurs·rices actifs·ves{" "}
                <br className="hidden md:block" />
                ces 10 dernières années sont des{" "}
              </span>
              <span className="text-violet-500">femmes</span>
            </span>
          </div>
          <Link href="/statistics">
            <Button className="bg-violet-500 cursor-pointer">
              Voir les statistiques
            </Button>
          </Link>
        </div>
      </main>
    </>
  );
}
