"use client";

import { useState } from "react";
import Link from "next/link";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  return (
    <nav className="bg-gray-800 text-white">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Link href="/" className="font-bold text-xl">
              CinéData
            </Link>
          </div>

          {/* Menu desktop */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-center space-x-4">
              <Link href="/" className="hover:bg-gray-700 px-3 py-2 rounded-md">
                Accueil
              </Link>
              <Link
                href="/films"
                className="hover:bg-gray-700 px-3 py-2 rounded-md"
              >
                Films
              </Link>
              <Link
                href="/festivals"
                className="hover:bg-gray-700 px-3 py-2 rounded-md"
              >
                Festivals
              </Link>
              <Link
                href="/about"
                className="hover:bg-gray-700 px-3 py-2 rounded-md"
              >
                À propos
              </Link>
              <Link
                href="/dashboard"
                className="hover:bg-gray-700 px-3 py-2 rounded-md"
              >
                Dashboard
              </Link>
            </div>
          </div>

          {/* Bouton menu mobile */}
          <div className="md:hidden">
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
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1">
            <Link
              href="/"
              className="block hover:bg-gray-700 px-3 py-2 rounded-md"
              onClick={toggleMenu}
            >
              Accueil
            </Link>
            <Link
              href="/films"
              className="block hover:bg-gray-700 px-3 py-2 rounded-md"
              onClick={toggleMenu}
            >
              Films
            </Link>
            <Link
              href="/festivals"
              className="block hover:bg-gray-700 px-3 py-2 rounded-md"
              onClick={toggleMenu}
            >
              Festivals
            </Link>
            <Link
              href="/about"
              className="block hover:bg-gray-700 px-3 py-2 rounded-md"
              onClick={toggleMenu}
            >
              À propos
            </Link>
            <Link
              href="/dashboard"
              className="block hover:bg-gray-700 px-3 py-2 rounded-md"
              onClick={toggleMenu}
            >
              Dashboard
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
