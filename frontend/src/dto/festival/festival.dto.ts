import { Metrics } from "./metrics.dto";

export type Festival = {
  id: number;
  name: string;
  description: string;
  date: string;
  image_base64: string;
  festival_metrics: Metrics;
};
