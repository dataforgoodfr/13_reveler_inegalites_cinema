import { ReducedFilm } from "./reduced-film.dto";

export type Nomination = {
  nomination_id: number;
  date: string;
  is_winner: boolean;
  film: ReducedFilm;
};
