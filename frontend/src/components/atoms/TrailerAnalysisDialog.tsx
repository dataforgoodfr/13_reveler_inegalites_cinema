"use client";

import { useRef, useState } from "react";
import { Button } from "../ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";

const TrailerAnalysisDialog = ({
  filmName,
  releaseDate,
  trailerUrl,
}: {
  filmName: string;
  releaseDate: string;
  trailerUrl: string;
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [duration, setDuration] = useState(0);

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      const videoDuration = videoRef.current.duration;
      setDuration(videoDuration);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    const minPart = mins ? `${mins} ${mins > 1 ? 'minutes' : 'minute'}` : '';
    const secPart = secs ? `${secs} ${secs > 1 ? 'secondes' : 'seconde'}` : '';
    return [minPart, secPart].filter(Boolean).join(' ');
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="icon" style={{ opacity: 0.8 }}>
          <img
            src="/video_search.svg"
            alt="Rechercher"
            width={24}
            height={24}
          />
        </Button>
      </DialogTrigger>
      <DialogContent
        className="border-0 text-white"
        style={{ backgroundColor: "rgb(30,30,30)", width: "60%", height: "80%", maxWidth: 'unset' }}
      >
        <DialogHeader className="items-center text-center p-5 h-full">
          <DialogTitle className="font-bold">
            {filmName} Bande Annonce {releaseDate.split("-")[0]}
          </DialogTitle>
          <div className="flex flex-col items-center justify-around h-full">
            <span>Durée de la bande annonce: </span>
            <span className="text-violet-500 font-semibold">
              {formatTime(duration)}
            </span>
            <video
              className="w-2/5 border-3 border-white"
              ref={videoRef}
              onLoadedMetadata={handleLoadedMetadata}
              src={trailerUrl}
              controls
            >
              Votre navigateur ne supporte pas la lecture de vidéos.
            </video>
            <div className="flex font-bold gap-50">
              <div>
                <div>
                  <span>Temps d'écran des personnages perçus comme </span>
                  <span className="text-violet-500">femmes</span>
                </div>
                <span className="text-violet-500">{"30 secondes"}</span>
              </div>
              <div>
                <div>
                  <span>Temps d'écran des personnages perçus comme </span>
                  <span className="text-violet-500">non blancs</span>
                </div>
                <span className="text-violet-500">{"10 secondes"}</span>
              </div>
            </div>
          </div>
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
};

export default TrailerAnalysisDialog;
