import {Algorithm} from "../../entities/Algorithm";
import {AlgorithmSynchronization} from "../../entities/AlgorithmSynchronization";
import {AlgorithmSecurity} from "../../entities/AlgorithmSecurity";

export interface TimeWhenVaryingParamNRequest {
    d : number;
    K : number;
    M : number;
    algorithm : Algorithm;
    algorithm_security : AlgorithmSecurity;
}
