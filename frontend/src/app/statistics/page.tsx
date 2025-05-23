"use client";

import { API_URL } from "@/utils/api-url";
import { useEffect, useState } from "react";

export default function StatisticsPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [iFrameUrl, setIFrameUrl] = useState('');

  useEffect(() => {
    const url = `${API_URL}/metabase/iframe-url`;
    fetch(url)
      .then((response) => {
        if (response.ok) {
          return response.json();
        }
        throw new Error("Fetch error");
      })
      .then((value: {iframe_url: string}) => {
        setIFrameUrl(value.iframe_url);
        setIsLoading(false);
      })
      .catch(() => {
        setHasError(true);
        setIsLoading(false);
      });
  }, []);

  if (isLoading || !iFrameUrl) {
    return (
      <main className="p-40 bg-transparent text-white flex justify-center items-center">
        <p>Chargement...</p>
      </main>
    );
  }

  if (hasError) {
    return (
      <main className="p-40 bg-transparent text-white flex justify-center items-center">
        <h1 className="text-4xl font-bold">Une erreur est survenue lors de la récupération des statistiques</h1>
      </main>
    );
  }

  return (
    <main className="flex flex-col items-center justify-center bg-gray-950 text-white">
      <div className="p-10 pt-40 w-full">
        <h1 className="pl-5 text-4xl font-bold">Statistiques</h1>
        <iframe
          src={iFrameUrl}
          width="100%"
          height="1650px"
          allowFullScreen
        />
      </div>
    </main>
  );
}
