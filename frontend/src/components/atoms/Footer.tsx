"use client";

import { ExternalLink } from "lucide-react";
import Image from "next/image";
import { Button } from "../ui/button";
import { useMediaQuery } from "@/hooks/useMediaQuery";

const Footer = () => {
const isMobile: boolean = useMediaQuery("(max-width: 768px)");

  return (
    <div className="px-5 md:px-15 py-5 w-full flex flex-col md:flex-row gap-10 bg-violet-700 text-white">
      <div className="flex flex-col md:flex-row gap-20 w-full justify-around">
        <div className="flex flex-col gap-5 md:gap-3 justify-center w-full">
          <Image
            src="/logo_5050.png"
            className="w-3/4 md:w-full"
            alt=""
            width={500}
            height={100}
          />
          <h1 className="font-bold">Collectif 50/50</h1>
          <a href="https://collectif5050.com" target="_blank" rel="noopener noreferrer" className="flex hover:underline">
            <p className="pr-2">Site internet</p>
            <ExternalLink />
          </a>
          <a href="https://collectif5050.com/nos-etudes/" target="_blank" rel="noopener noreferrer" className="flex hover:underline">
            <p className="pr-2">Nos études</p>
            <ExternalLink />
          </a>
          <div className="flex w-full py-2 justify-between">
            <a href="https://www.facebook.com/Collectif5050" target="_blank" rel="noopener noreferrer">
              <Image src="/facebook.png" alt="Facebook" width={isMobile ? 35 : 25} height={0} />
            </a>
            <a href="https://www.linkedin.com/company/le-collectif-50-50" target="_blank" rel="noopener noreferrer">
              <Image src="/linkedin.png" alt="Linkedin" width={isMobile ? 35 : 25} height={0} />
            </a>
            <a href="https://www.youtube.com/channel/UCWhSC21jayqFUXUoo02pLTA" target="_blank" rel="noopener noreferrer">
              <Image src="/youtube.png" alt="YouTube" width={isMobile ? 35 : 25} height={0} />
            </a>
            <a href="https://www.instagram.com/lecollectif5050/" target="_blank" rel="noopener noreferrer">
              <Image
                src="/instagram.png"
                alt="Instagram"
                width={isMobile ? 35 : 25}
                height={0}
              />
            </a>
          </div>
          <a href="https://www.helloasso.com/associations/collectif-50-50" target="_blank" rel="noopener noreferrer" className="w-full">
          <Button className="text-black bg-white hover:bg-grey w-full">
            Adhérer / Faire un don
          </Button>
          </a>
        </div>
        <div className="flex flex-col gap-5 md:gap-1 justify-center w-full pb-10">
          <Image src={"/logo_d4g.png"} alt="" width={70} height={0} />
          <h1 className="font-bold">Data for good</h1>
          <a href="https://dataforgood.fr/" target="_blank" rel="noopener noreferrer" className="flex hover:underline">
            <p className="pr-2">Site internet</p>
            <ExternalLink />
          </a>
          <a href="https://x.com/dataforgood_fr?lang=fr" target="_blank" rel="noopener noreferrer" className="flex hover:underline">
            <p className="pr-2">Twitter</p>
            <ExternalLink />
          </a>
          <a
            href="https://www.linkedin.com/company/dataforgood"
            className="flex hover:underline"
          >
            <p className="pr-2">LinkedIn</p>
            <ExternalLink />
          </a>
          <a href="mailto:contact@dataforgood.fr" className="flex hover:underline">
            <p className="pr-2">Envoyer un mail</p>
            <ExternalLink />
          </a>
        </div>
      </div>
      <div className="flex justify-center items-center font-bold w-full">
        <div className="bg-violet-700 border border-white/40 rounded-xl text-center p-4">
          Observatoire des inégalités dans le cinéma, <br />
          par le Collectif 50/50 et Data For Good
        </div>
      </div>
    </div>
  );
};

export default Footer;
