import { Nomination } from "./nomination.dto";

export type Award = {
  award_id: number;
  name: string;
  nominations: Nomination[];
};
