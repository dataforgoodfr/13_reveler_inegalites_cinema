"use client";

import { useRef, useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../ui/dialog";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle } from "../ui/drawer";
import {
  Carousel,
  CarouselContent,
  CarouselDots,
  CarouselItem,
} from "../ui/carousel";

const TrailerAnalysisDialog = ({
  open,
  setOpen,
  filmName,
  releaseDate,
  trailerUrl,
  femaleScreenTimeInTrailer,
  nonWhiteScreenTimeInTrailer,
}: {
  open: boolean;
  setOpen: (open: boolean) => void;
  filmName: string;
  releaseDate: string;
  trailerUrl?: string;
  femaleScreenTimeInTrailer?: number;
  nonWhiteScreenTimeInTrailer?: number;
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [duration, setDuration] = useState(0);
  const isMobile: boolean = useMediaQuery("(max-width: 768px)");

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      const videoDuration = videoRef.current.duration;
      setDuration(videoDuration);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.round(seconds / 60);
    const secs = Math.round(seconds % 60);
    const minPart = mins ? `${mins} ${mins > 1 ? "minutes" : "minute"}` : "";
    const secPart = secs ? `${secs} ${secs > 1 ? "secondes" : "seconde"}` : "";
    return [minPart, secPart].filter(Boolean).join(" ");
  };

  // Gestion des valeurs manquantes ou nulles
  const safeReleaseYear =
    releaseDate && releaseDate !== "null" ? releaseDate.split("-")[0] : "NC";
  const safeTrailerUrl =
    trailerUrl && trailerUrl !== "" ? trailerUrl : undefined;

  if (isMobile) {
    return (
      <Drawer open={open} onOpenChange={setOpen}>
        <DrawerContent
          className="border-0 text-white h-full"
          style={{
            backgroundColor: "rgb(30,30,30)",
          }}
        >
          <DrawerHeader className="items-center text-center p-5 h-full">
            <DrawerTitle className="font-bold text-white">
              {filmName ? filmName : "Titre inconnu"} Bande Annonce (
              {safeReleaseYear})
            </DrawerTitle>
            <Carousel className="w-full h-full">
              <CarouselContent className="h-full">
                <CarouselItem>
                  <div className="flex flex-col items-center h-full gap-5">
                    <span>Durée de la bande annonce: </span>
                    <span className="text-violet-500 font-semibold">
                      {duration > 0 ? formatTime(duration) : "NC"}
                    </span>
                    {safeTrailerUrl ? (
                      <video
                        className="w-4/5 border-3 border-white"
                        ref={videoRef}
                        onLoadedMetadata={handleLoadedMetadata}
                        src={safeTrailerUrl}
                        controls
                      >
                        Votre navigateur ne supporte pas la lecture de vidéos.
                      </video>
                    ) : (
                      <span className="text-white">
                        Aucune bande-annonce disponible.
                      </span>
                    )}
                  </div>
                </CarouselItem>
                <CarouselItem>
                  <div className="font-bold gap-50 text-left">
                    <div>
                      <div>
                        <span>
                          Temps d&apos;écran des personnages perçus comme{" "}
                        </span>
                        <span className="text-violet-500">femmes</span>
                      </div>
                      <span className="text-violet-500">
                        {typeof femaleScreenTimeInTrailer === "number"
                          ? formatTime(femaleScreenTimeInTrailer)
                          : "NC"}
                      </span>
                    </div>
                    <div>
                      <div>
                        <span>
                          Temps d&apos;écran des personnages perçus comme{" "}
                        </span>
                        <span className="text-violet-500">non blancs</span>
                      </div>
                      <span className="text-violet-500">
                        {typeof nonWhiteScreenTimeInTrailer === "number"
                          ? formatTime(nonWhiteScreenTimeInTrailer)
                          : "NC"}
                      </span>
                    </div>
                  </div>
                </CarouselItem>
              </CarouselContent>
              <CarouselDots className="absolute bottom-0 w-full" />
            </Carousel>
          </DrawerHeader>
        </DrawerContent>
      </Drawer>
    );
  }
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent
        className="border-0 text-white max-h-[90vh]"
        style={{
          backgroundColor: "rgb(30,30,30)",
          width: "800px",
          height: "500px",
          maxWidth: "unset",
        }}
      >
        <DialogHeader className="items-center text-center p-5 h-full">
          <DialogTitle className="font-bold">
            {filmName ? filmName : "Titre inconnu"} Bande Annonce{" "}
            {safeReleaseYear}
          </DialogTitle>
          <div className="flex flex-col items-center justify-around h-full">
            <span>Durée de la bande annonce: </span>
            <span className="text-violet-500 font-semibold">
              {duration > 0 ? formatTime(duration) : "NC"}
            </span>
            {safeTrailerUrl ? (
              <video
                className="w-2/5 border-3 border-white"
                ref={videoRef}
                onLoadedMetadata={handleLoadedMetadata}
                src={safeTrailerUrl}
                controls
              >
                Votre navigateur ne supporte pas la lecture de vidéos.
              </video>
            ) : (
              <span className="text-white">
                Aucune bande-annonce disponible.
              </span>
            )}
            <div className="flex font-bold gap-50">
              <div>
                <div>
                  <span>Temps d&apos;écran des personnages perçus comme </span>
                  <span className="text-violet-500">femmes</span>
                </div>
                <span className="text-violet-500">
                  {typeof femaleScreenTimeInTrailer === "number"
                    ? formatTime(femaleScreenTimeInTrailer)
                    : "NC"}
                </span>
              </div>
              <div>
                <div>
                  <span>Temps d&apos;écran des personnages perçus comme </span>
                  <span className="text-violet-500">non blancs</span>
                </div>
                <span className="text-violet-500">
                  {typeof nonWhiteScreenTimeInTrailer === "number"
                    ? formatTime(nonWhiteScreenTimeInTrailer)
                    : "NC"}
                </span>
              </div>
            </div>
          </div>
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
};

export default TrailerAnalysisDialog;
