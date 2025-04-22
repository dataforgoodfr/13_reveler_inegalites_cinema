import { Credits } from "./credits.dto";
import { Metrics } from "./metrics.dto";
import { Award } from "./award.dto";

export type Film = {
  id: number;
  original_name: string;
  release_date: string;
  duration: string;
  countries_sorted_by_budget: string[];
  genres: string[];
  poster_image_base64: string;
  parity_bonus: boolean;
  budget: number;
  metrics: Metrics;
  credits: Credits;
  awards: Award[];
  trailer_url?: string;
  first_language: string;
  cnc_agrement_year: number;
};
