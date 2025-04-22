export type ReducedFilm = {
  id: number;
  original_name: string;
  release_date: string;
  poster_image_base64: string;
  director: string[];
  female_representation_in_key_roles?: number;
  female_representation_in_casting?: number | null;
};
