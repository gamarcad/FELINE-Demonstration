import {Algorithm} from "../../entities/Algorithm";
import {AlgorithmSecurity} from "../../entities/AlgorithmSecurity";

export interface ComponentExecutionTimeBySynchronizationRequest {
    N : number;
    K : number;
    M : number;
    d : number;
    algorithm : Algorithm;
    algorithm_security : AlgorithmSecurity;
}
