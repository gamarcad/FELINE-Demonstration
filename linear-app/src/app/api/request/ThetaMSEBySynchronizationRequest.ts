import {Algorithm} from "../../entities/Algorithm";

export interface ThetaMSEBySynchronizationRequest {
    N : number;
    K : number;
    M : number;
    d : number;
    algorithm : Algorithm;
    algorithm_security : string;
    iteration : string;
}
