import { Credit } from "./credit.dto";
import { Distribution } from "./distribution.dto";

export type Credits = {
  key_roles: Credit[];
  distribution: Distribution;
  casting: Credit[];
};
