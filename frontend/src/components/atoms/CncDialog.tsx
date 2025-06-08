"use client";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
} from "../ui/drawer";
const CncDialog = ({
  open,
  setOpen
}: {
  open: boolean;
  setOpen: (open: boolean) => void;
}) => {
  const isMobile: boolean = useMediaQuery("(max-width: 768px)");

  if (isMobile) {
    return (
      <Drawer open={open} onOpenChange={setOpen}>
        <DrawerContent
          className="border-0 text-white px-5"
          style={{
            borderColor: "rgba(51, 51, 51, 1)",
            backgroundColor: "rgba(30, 30, 30)",
          }}
        >
          <DrawerHeader className="items-center p-5 h-full">
            <DrawerTitle className="font-bold text-center text-white">
              Bonus parité du CNC
            </DrawerTitle>
            <DrawerDescription className="text-white">
            Créé en 2019, ce bonus de 15% sur le soutien cinéma mobilisé
            s’adresse aux films d’initiative française dont les équipes sont
            paritaires au sein de leurs principaux postes d’encadrement, que la
            réalisation soit entre les mains d’un homme ou d’une femme.
            </DrawerDescription>
          </DrawerHeader>
        </DrawerContent>
      </Drawer>
    );
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent
        className="sm:max-w-[425px] text-white"
        style={{
          borderColor: "rgba(51, 51, 51, 1)",
          backgroundColor: "rgba(30, 30, 30)",
        }}
      >
        <DialogHeader>
          <DialogTitle>Bonus parité du CNC</DialogTitle>
          <DialogDescription className="text-white">
            Créé en 2019, ce bonus de 15% sur le soutien cinéma mobilisé
            s’adresse aux films d’initiative française dont les équipes sont
            paritaires au sein de leurs principaux postes d’encadrement, que la
            réalisation soit entre les mains d’un homme ou d’une femme.
          </DialogDescription>
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
};

export default CncDialog;
