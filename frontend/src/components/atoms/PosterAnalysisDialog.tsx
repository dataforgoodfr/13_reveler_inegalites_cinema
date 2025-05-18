"use client";

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../ui/dialog";
import {
  Carousel,
  CarouselContent,
  CarouselDots,
  CarouselItem,
} from "../ui/carousel";
import Image from "next/image";
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle } from "../ui/drawer";
import { useMediaQuery } from "@/hooks/useMediaQuery";

const PosterAnalysisDialog = ({
  open,
  setOpen,
  imageSource,
  femaleVisibleRatioOnPoster,
  nonWhiteVisibleRatioOnPoster,
}: {
  open: boolean;
  setOpen: (open: boolean) => void;
  imageSource: string;
  femaleVisibleRatioOnPoster?: number;
  nonWhiteVisibleRatioOnPoster?: number;
}) => {
  const isMobile: boolean = useMediaQuery("(max-width: 768px)");
  const safeImageSource =
    imageSource && imageSource !== "" ? imageSource : undefined;

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
              Analyse de l&apos;affiche
            </DrawerTitle>
            <Carousel className="w-full h-full">
              <CarouselContent className="h-full">
                <CarouselItem>
                  <div className="w-full flex justify-center">
                    <div
                      className="relative w[300px]"
                      style={{
                        backgroundColor: "rgba(30, 30, 30, 0.8)",
                        width: 300,
                        height: 380,
                        minHeight: 380,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      {safeImageSource ? (
                        <Image
                          loader={() => safeImageSource}
                          style={{ height: "fit-content" }}
                          src={safeImageSource}
                          alt="Affiche"
                          width={300}
                          height={0}
                        />
                      ) : (
                        <span className="text-white">
                          Affiche non disponible
                        </span>
                      )}
                      <div className="absolute inset-0 bg-black/60"></div>
                      <div className="absolute bottom-0 flex flex-col p-2 text-left font-bold break-words w-full">
                        <span className="text-violet-500 text-6xl">
                          {typeof femaleVisibleRatioOnPoster === "number"
                            ? `${femaleVisibleRatioOnPoster.toPrecision(2)}%`
                            : "NC"}
                        </span>
                        <span className="text-white text-l">
                          Part de personnages perçus comme femmes
                        </span>
                      </div>
                    </div>
                  </div>
                </CarouselItem>
                <CarouselItem>
                  <div className="w-full flex justify-center">
                    <div
                      className="relative w[300px]"
                      style={{
                        backgroundColor: "rgba(30, 30, 30, 0.8)",
                        width: 300,
                        height: 380,
                        minHeight: 380,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      {safeImageSource ? (
                        <Image
                          loader={() => safeImageSource}
                          style={{ height: "fit-content" }}
                          src={safeImageSource}
                          alt="Affiche"
                          width={300}
                          height={0}
                        />
                      ) : (
                        <span className="text-white">
                          Affiche non disponible
                        </span>
                      )}
                      <div className="absolute inset-0 bg-black/60"></div>
                      <div className="absolute bottom-0 flex flex-col p-2 text-left font-bold break-words w-full">
                        <span className="text-violet-500 text-6xl">
                          {typeof nonWhiteVisibleRatioOnPoster === "number"
                            ? `${nonWhiteVisibleRatioOnPoster.toPrecision(2)}%`
                            : "NC"}
                        </span>
                        <span className="text-white text-l">
                          Part de personnages perçus comme non blancs
                        </span>
                      </div>
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
                        width: 300,
                        height: 380,
                        minHeight: 380,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      {safeImageSource ? (
                        <Image
                          loader={() => safeImageSource}
                          style={{
                            height: "fit-content",
                            objectFit: "cover",
                            maxHeight: "50vh",
                          }}
                          src={safeImageSource}
                          alt="Affiche"
                          width={300}
                          height={0}
                        />
                      ) : (
                        <span className="text-white">
                          Affiche non disponible
                        </span>
                      )}
                      <div className="absolute inset-0 bg-black/60"></div>
                      <div className="absolute bottom-0 flex flex-col p-2">
                        <span className="text-violet-500 text-left text-6xl font-bold">
                          {typeof femaleVisibleRatioOnPoster === "number"
                            ? `${femaleVisibleRatioOnPoster.toPrecision(2)}%`
                            : "NC"}
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
                        width: 300,
                        height: 380,
                        minHeight: 380,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      {safeImageSource ? (
                        <Image
                          loader={() => safeImageSource}
                          style={{
                            height: "fit-content",
                            objectFit: "cover",
                            maxHeight: "50vh",
                          }}
                          src={safeImageSource}
                          alt="Affiche"
                          width={300}
                          height={0}
                        />
                      ) : (
                        <span className="text-white">
                          Affiche non disponible
                        </span>
                      )}
                      <div className="absolute inset-0 bg-black/60"></div>
                      <div className="absolute bottom-0 flex flex-col p-2">
                        <span className="text-violet-500 text-left text-6xl font-bold">
                          {typeof nonWhiteVisibleRatioOnPoster === "number"
                            ? `${nonWhiteVisibleRatioOnPoster.toPrecision(2)}%`
                            : "NC"}
                        </span>
                        <span className="text-white text-left text-l font-bold">
                          Part de personnages perçus comme non blancs
                        </span>
                      </div>
                    </div>
                  </CarouselItem>
                </CarouselContent>
                <CarouselDots />
              </Carousel>
            </div>
          </div>
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
};

export default PosterAnalysisDialog;
