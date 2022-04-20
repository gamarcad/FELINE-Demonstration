import {CumulativeExecutionTime} from "./CumulativeExecutionTime";

export interface CumulativeExecutionTimeBySynchronization {
    "no-sync": CumulativeExecutionTime,
    "four-steps" : CumulativeExecutionTime,
    "two-steps" : CumulativeExecutionTime,
    "each-step" : CumulativeExecutionTime,
}
