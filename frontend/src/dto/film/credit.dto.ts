export type Credit = {
  name: string;
  role: string;
  gender?: "male" | "female" | string;
  is_key_role: boolean;
  is_company: boolean;
};
