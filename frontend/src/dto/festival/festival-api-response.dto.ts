import { Award } from "./award.dto";
import { ReducedAward } from "./reduced-award.dto";
import { Festival } from "./festival.dto";

export type FestivalApiResponse = {
  festival: Festival;
  year: number;
  available_years: number[];
  award: Award;
  available_awards: ReducedAward[];
};
