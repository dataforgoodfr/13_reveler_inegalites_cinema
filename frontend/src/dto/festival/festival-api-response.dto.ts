import { Award } from "./award.dto";
import { Festival } from "./festival.dto";

export type FestivalApiResponse = {
  festival: {
    festival: Festival;
    awards: Award[];
  }
};
