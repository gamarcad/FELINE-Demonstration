import {ComponentExecutionTime} from "./ComponentExecutionTime";

export interface ComponentExecutionTimeBySynchronization {
    "no-sync": ComponentExecutionTime,
    "four-steps": ComponentExecutionTime,
    "two-steps": ComponentExecutionTime,
    "each-step": ComponentExecutionTime,
}
