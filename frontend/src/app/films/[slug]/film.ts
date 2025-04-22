export type Film = {
  id: number;
  original_name: string;
  release_date: string;
  first_language: string;
  parity_bonus: boolean;
  cnc_agrement_year: number;
  budget: number;
  duration: string;
  genres: string[];
  poster_image_base64: string;
  trailer_url: string;
  countries_sorted_by_budget: string[];
  credits: {
    casting: Credit[];
    key_roles: Credit[];
    distribution: Credit[];
  };
  awards: Award[];
  metrics: FilmMetrics;
};

export type Credit = {
  role: string;
  is_key_role: boolean;
  is_company: boolean;
  name: string;
  gender: "male" | "female" | null;
};

export type Award = {
  festival_id: number;
  festival_name: string;
  award_name: string;
  date: string;
  is_winner: boolean;
};

export type FilmMetrics = {
  female_representation_in_key_roles: number;
  female_representation_in_casting: number;
  female_screen_time_in_trailer: number;
  non_white_screen_time_in_trailer: number;
  female_visible_ratio_on_poster: number;
  non_white_visible_ratio_on_poster: number;
};