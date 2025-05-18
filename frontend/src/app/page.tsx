import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function Home() {
  return (
    <>
      <div
        className="background-image"
        style={
          {
            "--background-image-url": `url('/home.jpeg')`,
          } as React.CSSProperties
        }
      ></div>
      <main className="container mx-auto px-4 py-16 flex flex-col items-center justify-center text-center text-white">
        <div className=" animate-slide-up">
          <div className="pt-30 pb-5">
            <span className="text-6xl font-bold w-3/4">
              <span className="text-violet-500">27%</span>
              <span> des réalisateurs actifs ces 10 dernières années sont des </span>
              <span className="text-violet-500">femmes</span>
            </span>
          </div>
          <Link href="/statistics">
            <Button className="bg-violet-500">Voir les statistiques</Button>
          </Link>
        </div>
      </main>
    </>
  );
}
