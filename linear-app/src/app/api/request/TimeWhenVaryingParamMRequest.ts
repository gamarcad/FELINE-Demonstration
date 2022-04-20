import {Algorithm} from "../../entities/Algorithm";
import {AlgorithmSynchronization} from "../../entities/AlgorithmSynchronization";
import {AlgorithmSecurity} from "../../entities/AlgorithmSecurity";

export interface TimeWhenVaryingParamMRequest {
    N : number;
    K : number;
    d : number;
    algorithm : Algorithm;
    algorithm_security : AlgorithmSecurity;
}
