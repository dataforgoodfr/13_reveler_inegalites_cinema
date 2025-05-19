"use client";

import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog";
import Image from "next/image";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import { Drawer, DrawerContent, DrawerDescription, DrawerFooter, DrawerHeader, DrawerTitle } from "../ui/drawer";

const ShareDialog = ({
  open,
  setOpen,
  imageSource
}: {
  open: boolean;
  setOpen: (open: boolean) => void;
  imageSource: string;
}) => {
  const shareUrl = window?.location.href;
  const shareText = "Découvrez ce film incroyable !";

  const copyLink = () => {
    navigator.clipboard.writeText(shareUrl);
    toast("Lien copié dans le presse-papier !", {
      description: "Sunday, December 03, 2023 at 9:00 AM",
      action: {
        label: "Undo",
        onClick: () => console.log("Undo"),
      },
    });
  };

  const openSocialShare = (platform: string) => {
    const encodedUrl = encodeURIComponent(shareUrl);
    const encodedText = encodeURIComponent(shareText);
    let shareLink = "";

    switch (platform) {
      case "mail":
        shareLink = `mailto:?subject=${encodedText}&body=${encodedUrl}`;
        break;
      case "instagram":
        alert("Instagram ne supporte pas le partage direct via URL.");
        return;
      case "twitter":
        shareLink = `https://twitter.com/intent/tweet?text=${encodedText}&url=${encodedUrl}`;
        break;
      case "whatsapp":
        shareLink = `https://wa.me/?text=${encodedText}%20${encodedUrl}`;
        break;
      default:
        return;
    }

    window.open(shareLink, "_blank");
  };
  const isMobile: boolean = useMediaQuery("(max-width: 768px)");
  const safeImageSource = imageSource && imageSource !== "" ? imageSource : undefined;

  if (isMobile) {
    return (
      <Drawer open={open} onOpenChange={setOpen}>
        <DrawerContent
          className="border-0 text-white"
          style={{
            backgroundColor: "rgb(30,30,30)",
          }}
        >
          <DrawerHeader className="items-center text-center p-5 h-full">
          <DrawerTitle className="font-bold text-white">Partager le film</DrawerTitle>
          <DrawerDescription>
            {safeImageSource ? (
              <Image
                loader={() => imageSource}
                style={{ height: "fit-content", maxHeight: "50vh", objectFit: "contain" }}
                src={imageSource}
                alt="Affiche"
                width={257.45}
                height={0}
              />
            ) : (
              <Image
                style={{ height: "fit-content" }}
                src="/placeholder_image.svg"
                alt="Image indisponible"
                width={257.45}
                height={0}
              />
            )}
          </DrawerDescription>
          <DrawerFooter className="flex flex-row justify-between">
            <div
              className="flex flex-col items-center flex-1 text-xs text-center cursor-pointer relative"
              onClick={copyLink}
            >
              <Image src="/copy_link.svg" alt="Copier le lien" height={48} width={48}/>
              <span>Copier le lien</span>
            </div>
            <div
              className="flex flex-col items-center flex-1 text-xs text-center cursor-pointer relative"
              onClick={() => openSocialShare("mail")}
            >
              <Image src="/mail.svg" alt="Mail" height={48} width={48}/>
              <span>Mail</span>
            </div>
            <div
              className="flex flex-col items-center flex-1 text-xs text-center cursor-pointer relative"
              onClick={() => openSocialShare("instagram")}
            >
              <Image src="/instagram.svg" alt="Instagram" height={48} width={48}/>
              <span>Instagram</span>
            </div>
            <div
              className="flex flex-col items-center flex-1 text-xs text-center cursor-pointer relative"
              onClick={() => openSocialShare("twitter")}
            >
              <Image src="/twitter.svg" alt="Twitter" height={48} width={48}/>
              <span>Twitter</span>
            </div>
            <div
              className="flex flex-col items-center flex-1 text-xs text-center cursor-pointer relative"
              onClick={() => openSocialShare("whatsapp")}
            >
              <Image src="/whatsapp.svg" alt="WhatsApp" height={48} width={48}/>
              <span>WhatsApp</span>
            </div>
          </DrawerFooter>
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
        <DialogHeader className="items-center text-center">
          <DialogTitle>Partager le film</DialogTitle>
          <DialogDescription>
            {safeImageSource ? (
              <Image
                loader={() => imageSource}
                style={{ height: "fit-content", maxHeight: "50vh", objectFit: "contain" }}
                src={imageSource}
                alt="Affiche"
                width={257.45}
                height={0}
              />
            ) : (
              <Image
                style={{ height: "fit-content" }}
                src="/placeholder_image.svg"
                alt="Image indisponible"
                width={257.45}
                height={0}
              />
            )}
          </DialogDescription>
          <DialogFooter className="flex flex-row justify-between">
            <div
              className="flex flex-col items-center flex-1 text-xs text-center cursor-pointer relative"
              onClick={copyLink}
            >
              <Image src="/copy_link.svg" alt="Copier le lien" height={48} width={48}/>
              <span>Copier le lien</span>
            </div>
            <div
              className="flex flex-col items-center flex-1 text-xs text-center cursor-pointer relative"
              onClick={() => openSocialShare("mail")}
            >
              <Image src="/mail.svg" alt="Mail" height={48} width={48}/>
              <span>Mail</span>
            </div>
            <div
              className="flex flex-col items-center flex-1 text-xs text-center cursor-pointer relative"
              onClick={() => openSocialShare("instagram")}
            >
              <Image src="/instagram.svg" alt="Instagram" height={48} width={48}/>
              <span>Instagram</span>
            </div>
            <div
              className="flex flex-col items-center flex-1 text-xs text-center cursor-pointer relative"
              onClick={() => openSocialShare("twitter")}
            >
              <Image src="/twitter.svg" alt="Twitter" height={48} width={48}/>
              <span>Twitter</span>
            </div>
            <div
              className="flex flex-col items-center flex-1 text-xs text-center cursor-pointer relative"
              onClick={() => openSocialShare("whatsapp")}
            >
              <Image src="/whatsapp.svg" alt="WhatsApp" height={48} width={48}/>
              <span>WhatsApp</span>
            </div>
          </DialogFooter>
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
};

export default ShareDialog;
