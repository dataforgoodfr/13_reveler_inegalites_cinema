"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { usePathname } from "next/navigation";
import { SearchFilmResultDto } from "@/dto/film/search-film-result.dto";
import Image from "next/image";
import { API_URL } from "@/utils/api-url";
import { nameToUpperCase } from "@/utils/name-to-uppercase";

const Navbar = ({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) => {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [searchQuery, setSearchQuery] = useState(""); // État pour l'input de recherche
  const [filteredFilms, setFilteredFilms] = useState<SearchFilmResultDto[]>([]); // État pour les résultats filtrés

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const handleSearch = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value.toLowerCase();
    setSearchQuery(query);
    if (query) {
      try {
        const url = `${API_URL}/search?q=${query}`;
        const response = await fetch(url); // Default mode (CORS enabled on backend)

        if (!response.ok) {
          throw new Error(`Erreur HTTP ! statut : ${response.status}`);
        }

        const data: SearchFilmResultDto[] = await response.json();
        setFilteredFilms(data.map(dat => {return {...dat, directors: ['alexandre de la patellière']}}));
      } catch (error) {
        console.error("Erreur lors de la recherche :", error);
      }
    } else {
      setFilteredFilms([]);
    }
  };

  return (
    <>
      {isSearching ? (
        <div className="absolute mx-auto px-4 w-full">
          {/* Overlay pour masquer le contenu en dessous */}
          <div
            className="fixed inset-0 bg-grey bg-opacity-50 backdrop-blur-xl z-10"
            onClick={() => {
              setSearchQuery("");
              setIsSearching(false);
              setFilteredFilms([]);
            }} // Réinitialiser la recherche après un clic
          />

          {/* Champ de recherche */}
          <div className="relative py-5 z-20 rounded-md">
            <Input
              type="text"
              placeholder="Rechercher un film ou un festival..."
              value={searchQuery}
              onChange={handleSearch}
              className="px-3 py-5 rounded-md text-black bg-white"
              autoFocus
            />
            {filteredFilms.length > 0 && (
              <>
                <p className="px-2 py-3 text-white">Films</p>
                <div className="absolute mt-2 rounded-md w-full">
                  {filteredFilms.map((film) => (
                    <Link
                      key={film.id}
                      href={`/films/${film.id}`}
                      className="block px-4 py-2 hover:bg-gray-200 hover:text-black rounded-md"
                      onClick={() => {
                        setSearchQuery("");
                        setIsSearching(false);
                        setFilteredFilms([]);
                      }} // Réinitialiser la recherche après un clic
                    >
                      <div className="flex text-white hover:text-black relative">
                        {film.image && film.image !== "" ? (
                          <Image
                            loader={() => film.image}
                            src={film.image}
                            alt={film.title}
                            className="w-16 h-24 object-cover rounded-md mr-2"
                            width={32}
                            height={48}
                          />
                        ) : (
                          <div
                            className="relative w-16 h-24 rounded-md mr-2"
                            style={{backgroundColor: '#d0d0d0'}}
                          >
                            <Image
                              src="/placeholder_image.svg"
                              alt="Image indisponible"
                              fill
                            />
                          </div>
                        )}
                        <div className="flex flex-col">
                          <span>
                            <strong className="text-xl">{film.title}</strong> (
                            {film.year})
                          </span>
                          <span>
                            Réalisé par{" "}
                            <strong>{film.directors.map(nameToUpperCase).join(", ")}</strong>
                          </span>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      ) : (
        <nav
          className={`text-white absolute w-full z-10 ${
            isOpen ? "flex flex-col h-full bg-zinc-800" : ""
          } md:bg-transparent`}
        >
          {["/", "/statistics"].includes(pathname) && !isOpen && (
            <div
              className="absolute mx-16 cursor-pointer"
              style={{
                width: "230px",
                paddingTop: "20px",
              }}
            >
              <Link href="/" className="font-bold text-xl">
                Observatoire de l’inclusion et de l’équité dans l’industrie du
                cinéma, par le Collectif 50/50 et Data For Good
              </Link>
            </div>
          )}
          <div className="mx-auto px-4 w-full">
            <div className="flex items-center justify-end h-16">
              {/* Menu desktop */}
              <div className="hidden md:block">
                <div className="ml-10 flex items-center space-x-4">
                  <Link
                    href="/"
                    className="px-3 py-2 rounded-md cursor-pointer"
                  >
                    Accueil
                  </Link>
                  <Link
                    href="/statistics"
                    className="px-3 py-2 rounded-md cursor-pointer"
                  >
                    Statistiques
                  </Link>
                  <Link
                    href="/about"
                    className="px-3 py-2 rounded-md cursor-pointer"
                  >
                    À propos
                  </Link>
                  <button
                    className="px-3 py-2 rounded-md cursor-pointer"
                    onClick={() => setIsSearching(!isSearching)}
                  >
                    <Image
                      src="/search.svg"
                      alt="Rechercher"
                      height={36}
                      width={36}
                    />
                  </button>
                  <Link href="/" className="px-3 py-2 rounded-md">
                    <Button className="cursor-pointer">
                      Donnez nous votre avis 💬
                    </Button>
                  </Link>
                </div>
              </div>

              {/* Bouton menu mobile */}
              <div className="md:hidden w-full flex flex-row justify-end">
                {!isOpen && (
                  <button
                    className="p-4 rounded-md relative"
                    onClick={() => setIsSearching(!isSearching)}
                  >
                    <Image src="/search.svg" alt="Rechercher" fill />
                  </button>
                )}
                <button
                  onClick={toggleMenu}
                  className="inline-flex items-center justify-center p-2 rounded-md hover:bg-gray-700 focus:outline-none"
                >
                  <svg
                    className="h-6 w-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    {isOpen ? (
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    ) : (
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 6h16M4 12h16M4 18h16"
                      />
                    )}
                  </svg>
                </button>
              </div>
            </div>
          </div>

          {isOpen && (
            <div className="md:hidden text-white h-full flex flex-col justify-between">
              <div className="px-2 pt-2 pb-3 space-y-1 h-full flex flex-col justify-center items-center">
                <Link
                  href="/"
                  className="block hover:bg-gray-700 px-3 py-2 rounded-md cursor-pointer"
                  onClick={toggleMenu}
                >
                  Accueil
                </Link>
                <Link
                  href="/statistics"
                  className="block hover:bg-gray-700 px-3 py-2 rounded-md cursor-pointer"
                  onClick={toggleMenu}
                >
                  Statistiques
                </Link>
                <Link
                  href="/about"
                  className="block hover:bg-gray-700 px-3 py-2 rounded-md cursor-pointer"
                  onClick={toggleMenu}
                >
                  À propos
                </Link>
              </div>
              <div className="px-2 pb-3">
                <Link
                  href="/"
                  className="block px-3 py-2 rounded-md"
                  onClick={toggleMenu}
                >
                  <Button className="w-full bg-white text-black hover:text-white cursor-pointer">
                    Donnez nous votre avis 💬
                  </Button>
                </Link>
              </div>
            </div>
          )}
        </nav>
      )}
      <div>{children}</div>
    </>
  );
};

export default Navbar;
