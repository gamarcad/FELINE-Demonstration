import {ComponentExecutionTime} from "./ComponentExecutionTime";

export interface ComponentExecutionTimeBySynchronization {
    "entities": string[]
    "no-sync": ComponentExecutionTime,
    "four-steps": ComponentExecutionTime,
    "two-steps": ComponentExecutionTime,
    "each-step": ComponentExecutionTime,
}
