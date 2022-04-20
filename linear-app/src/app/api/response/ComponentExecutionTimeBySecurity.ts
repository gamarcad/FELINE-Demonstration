import {ComponentExecutionTime} from "./ComponentExecutionTime";

export interface ComponentExecutionTimeBySecurity {
    "plaintext-version": ComponentExecutionTime,
    "masked-version": ComponentExecutionTime
}
