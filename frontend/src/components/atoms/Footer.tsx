"use client";

import Image from "next/image";
import Link from "next/link";
import { Button } from "../ui/button";
import { useMediaQuery } from "@/hooks/useMediaQuery";

const Footer = () => {
  const isMobile: boolean = useMediaQuery("(max-width: 768px)");

  return (
    <div className="px-5 md:px-15 py-5 w-full flex flex-col md:flex-row gap-10 bg-[#421F7A] text-white">
      <div className="flex flex-col md:flex-row gap-20 w-full justify-around">
        {!isMobile && (
          <div className="flex flex-col justify-around w-full">
            <Image
              src="/logo_5050.png"
              className="w-full"
              alt="Logo du collectif 50/50"
              width={500}
              height={0}
            />
            <Image src={"/logo_d4g.png"} alt="Logo Data For Good" width={70} height={0} />
          </div>
        )}
        <div className="flex flex-col gap-5 md:gap-3 justify-center w-full">
          {isMobile && (
            <Image
              src="/logo_5050.png"
              className="w-3/4 md:w-full"
              alt="Logo du collectif 50/50"
              width={500}
              height={100}
            />
          )}
          <h1 className="font-bold">Collectif 50/50</h1>
          <a
            href="https://collectif5050.com"
            target="_blank"
            rel="noopener noreferrer"
            className="flex text-[#BABFD6] hover:underline hover:text-white"
          >
            <p className="pr-2">Site internet</p>
          </a>
          <a
            href="https://collectif5050.com/nos-etudes/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex text-[#BABFD6] hover:underline hover:text-white"
          >
            <p className="pr-2">Nos études</p>
          </a>
          <div className="flex w-full py-2 justify-between">
            <a
              href="https://www.facebook.com/Collectif5050"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Image
                src="/facebook.png"
                alt="Facebook"
                width={isMobile ? 35 : 25}
                height={0}
              />
            </a>
            <a
              href="https://www.linkedin.com/company/le-collectif-50-50"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Image
                src="/linkedin.png"
                alt="Linkedin"
                width={isMobile ? 35 : 25}
                height={0}
              />
            </a>
            <a
              href="https://www.youtube.com/channel/UCWhSC21jayqFUXUoo02pLTA"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Image
                src="/youtube.png"
                alt="YouTube"
                width={isMobile ? 35 : 25}
                height={0}
              />
            </a>
            <a
              href="https://www.instagram.com/lecollectif5050/"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Image
                src="/instagram.png"
                alt="Instagram"
                width={isMobile ? 35 : 25}
                height={0}
              />
            </a>
          </div>
          <a
            href="https://www.helloasso.com/associations/collectif-50-50"
            target="_blank"
            rel="noopener noreferrer"
            className="w-full"
          >
            <Button className="text-black bg-white hover:bg-grey w-full cursor-pointer">
              Adhérer / Faire un don
            </Button>
          </a>
        </div>
        <div className="flex flex-col gap-5 w-full">
          {isMobile && (
            <Image src={"/logo_d4g.png"} alt="Logo Data For Good" width={70} height={0} />
          )}
          <h1 className="font-bold">Data For Good</h1>
          <a
            href="https://dataforgood.fr/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex text-[#BABFD6] hover:underline hover:text-white"
          >
            <p className="pr-2">Site internet</p>
          </a>
          <div className="flex w-full py-2 gap-5">
            <a
              href="https://bsky.app/profile/did:plc:k6f6wuz6wlj6pyprvataqgae"
              target="_blank"
              rel="noopener noreferrer"
              className="flex text-[#BABFD6] hover:underline hover:text-white"
            >
              <Image
                src="/bluesky.svg"
                alt="Bsky"
                width={isMobile ? 35 : 25}
                height={0}
              />
            </a>
            <a
              href="https://www.linkedin.com/company/dataforgood"
              target="_blank"
              rel="noopener noreferrer"
              className="flex text-[#BABFD6] hover:underline hover:text-white"
            >
              <Image
                src="/linkedin.png"
                alt="Linkedin"
                width={isMobile ? 35 : 25}
                height={0}
              />
            </a>
          </div>
        </div>
        <div className="flex flex-col justify-center w-full">
          <Link
            href="mailto:collectif5050x2020@gmail.com?subject=Cin%C3%A9stats%2050%2F50"
            className="rounded-md"
          >
            <Button className="bg-white text-black cursor-pointer hover:text-white">
              Donnez-nous votre avis 💬
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Footer;
