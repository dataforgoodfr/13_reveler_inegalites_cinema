import Link from "next/link";

export default function FilmsPage() {
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Page des Films</h1>
      <p className="mb-2">
        Ceci est la page Films utilisant le Router Next.js.
      </p>
      <div className="bg-gray-100 p-4 rounded-md">
        <h2 className="text-lg font-semibold mb-2">
          Informations sur le Routing :
        </h2>
        <ul className="list-disc pl-5">
          <li>
            Cette page se trouve à : <code>/films</code>
          </li>
          <li>
            Chemin du fichier : <code>src/app/films/page.tsx</code>
          </li>
          <li>
            Next.js gère automatiquement le routing basé sur la structure des
            fichiers
          </li>
          <li>
            Routes dynamiques exemple : <code>/films/[id]</code> pour{" "}
            <code>src/app/films/[id]/page.tsx</code>
          </li>
        </ul>
        <div className="mt-4">
          <h3 className="font-semibold mb-2">Exemples de liens dynamiques :</h3>
          <div className="space-x-4">
            <Link href="/films/1" className="text-blue-600 hover:underline">
              Film #1
            </Link>
            <Link href="/films/2" className="text-blue-600 hover:underline">
              Film #2
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
