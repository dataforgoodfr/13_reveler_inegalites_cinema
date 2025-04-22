"use client";

import { Button } from "../ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "../ui/carousel";
import Image from "next/image";

const PosterAnalysisDialog = ({
  imageSource,
  femaleVisibleRatioOnPoster,
  nonWhiteVisibleRatioOnPoster,
}: {
  imageSource: string;
  femaleVisibleRatioOnPoster: number;
  nonWhiteVisibleRatioOnPoster: number;
}) => {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="icon" style={{ opacity: 0.8 }}>
          <Image
            src="/frame_search.svg"
            alt="Rechercher"
            width={24}
            height={24}
          />
        </Button>
      </DialogTrigger>
      <DialogContent
        className="sm:max-w-[425px] border-0 text-white"
        style={{ backgroundColor: "rgb(30,30,30)" }}
      >
        <DialogHeader style={{ textAlign: "center", justifyContent: "center" }}>
          <DialogTitle>Analyse de l&apos;affiche</DialogTitle>
          <div className="w-full flex justify-center">
            <div className="w-3/4">
              <Carousel>
                <CarouselContent>
                  <CarouselItem>
                    <div
                      className="relative"
                      style={{
                        backgroundColor: "rgba(30, 30, 30, 0.8)",
                      }}
                    >
                      <Image
                        loader={() => imageSource}
                        style={{ height: "fit-content" }}
                        src={imageSource}
                        alt="Affiche"
                        width={300}
                        height={0}
                      />
                      <div className="absolute inset-0 bg-black/60"></div>
                      <div className="absolute bottom-0 flex flex-col p-2">
                        <span className="text-violet-500 text-left text-6xl font-bold">
                          {typeof femaleVisibleRatioOnPoster === 'number' ? `${femaleVisibleRatioOnPoster}%` : 'NC'}
                        </span>
                        <span className="text-white text-left text-l font-bold">
                          Part de personnages perçus comme femmes
                        </span>
                      </div>
                    </div>
                  </CarouselItem>
                  <CarouselItem>
                    <div
                      className="relative"
                      style={{
                        backgroundColor: "rgba(30, 30, 30, 0.8)",
                      }}
                    >
                      <Image
                        loader={() => imageSource}
                        style={{ height: "fit-content" }}
                        src={imageSource}
                        alt="Affiche"
                        width={300}
                        height={0}
                      />
                      <div className="absolute inset-0 bg-black/60"></div>
                      <div className="absolute bottom-0 flex flex-col p-2">
                        <span className="text-violet-500 text-left text-6xl font-bold">
                        {typeof nonWhiteVisibleRatioOnPoster === 'number' ? `${nonWhiteVisibleRatioOnPoster}%` : 'NC'}
                        </span>
                        <span className="text-white text-left text-l font-bold">
                          Part de personnages perçus comme non blancs
                        </span>
                      </div>
                    </div>
                  </CarouselItem>
                </CarouselContent>
                <CarouselPrevious style={{ color: "black" }} />
                <CarouselNext style={{ color: "black" }} />
              </Carousel>
            </div>
          </div>
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
};

export default PosterAnalysisDialog;
