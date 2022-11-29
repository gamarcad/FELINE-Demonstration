import {ComponentExecutionTime} from "./ComponentExecutionTime";

export interface ComponentExecutionTimeBySecurity {
    "entities": string[],
    "plaintext-version": ComponentExecutionTime,
    "masked-version": ComponentExecutionTime
}
