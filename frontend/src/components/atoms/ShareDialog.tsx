"use client";

import { toast } from "sonner";
import { Button } from "../ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";
import Image from "next/image";

const ShareDialog = ({ imageSource }: { imageSource: string }) => {
  const shareUrl = window.location.href;
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

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="icon" style={{ opacity: 0.8 }}>
          <Image src="/share.svg" alt="Rechercher" width={24} height={24} />
        </Button>
      </DialogTrigger>
      <DialogContent
        className="sm:max-w-[425px] border-0 text-white"
        style={{ backgroundColor: "rgb(30,30,30)" }}
      >
        <DialogHeader className="items-center text-center">
          <DialogTitle>Partager le film</DialogTitle>
          <DialogDescription>
            <Image
              style={{ height: "fit-content" }}
              src={imageSource}
              alt="Affiche"
              width={257.45}
            />
          </DialogDescription>
          <DialogFooter className="flex justify-between">
            <div
              className="flex flex-col items-center flex-1 text-xs text-center cursor-pointer"
              onClick={copyLink}
            >
              <Image src="/copy_link.svg" alt="Copier le lien" />
              <span>Copier le lien</span>
            </div>
            <div
              className="flex flex-col items-center flex-1 text-xs text-center cursor-pointer"
              onClick={() => openSocialShare("mail")}
            >
              <Image src="/mail.svg" alt="Mail" />
              <span>Mail</span>
            </div>
            <div
              className="flex flex-col items-center flex-1 text-xs text-center cursor-pointer"
              onClick={() => openSocialShare("instagram")}
            >
              <Image src="/instagram.svg" alt="Instagram" />
              <span>Instagram</span>
            </div>
            <div
              className="flex flex-col items-center flex-1 text-xs text-center cursor-pointer"
              onClick={() => openSocialShare("twitter")}
            >
              <Image src="/twitter.svg" alt="Twitter" />
              <span>Twitter</span>
            </div>
            <div
              className="flex flex-col items-center flex-1 text-xs text-center cursor-pointer"
              onClick={() => openSocialShare("whatsapp")}
            >
              <Image src="/whatsapp.svg" alt="WhatsApp" />
              <span>WhatsApp</span>
            </div>
          </DialogFooter>
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
};

export default ShareDialog;
