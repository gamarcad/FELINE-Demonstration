import {TimeWhileVaryingParameter} from "./TimeWhileVaryingParameter";

export interface TimeWhileVaryingParameterBySynchronization {
    "no-sync": TimeWhileVaryingParameter;
    "each-step": TimeWhileVaryingParameter,
    "two-steps": TimeWhileVaryingParameter,
    "four-steps": TimeWhileVaryingParameter,
}
