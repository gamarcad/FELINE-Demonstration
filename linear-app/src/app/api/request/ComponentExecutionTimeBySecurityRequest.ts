import {Algorithm} from "../../entities/Algorithm";
import {AlgorithmSynchronization} from "../../entities/AlgorithmSynchronization";

export interface ComponentExecutionTimeBySecurityRequest {
    N : number;
    K : number;
    M : number;
    d : number;
    algorithm : Algorithm;
    algorithm_synchronization : AlgorithmSynchronization;
    iteration : string;
}
