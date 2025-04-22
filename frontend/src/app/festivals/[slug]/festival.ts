export type Festival = {
  id: number;
  name: string;
  description: string;
  date: string;
  image_base64: string;
  festival_metrics: FestivalMetric;
};

export type Award = {
  award_id: number;
  name: string;
  nominations: Nomination[];
};

export type Nomination = {
  nomination_id: number;
  date: string;
  is_winner: boolean;
  film: ReducedFilm;
};

type ReducedFilm = {
  id: number;
  original_name: string;
  release_date: string;
  poster_image_base64: string;
  director: string[];
  female_representation_in_key_roles?: number;
  female_representation_in_casting?: number | null;
};

type FestivalMetric = {
  prizes_awarded_to_women: {
    [year: number]: number;
  };
  produced_by_women: {
    [year: number]: number;
  };
}