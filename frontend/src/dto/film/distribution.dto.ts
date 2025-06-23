import { Credit } from "./credit.dto";

export type Distribution = {
  distribution: Credit[],
  production: Credit[],
  'co-production': Credit[],
  financiers: Credit[],
  budget: number
};
