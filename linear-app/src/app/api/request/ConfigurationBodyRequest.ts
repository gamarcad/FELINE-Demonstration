import {Algorithm} from "../../entities/Algorithm";

export interface ConfigurationBodyRequest {
    N : number;
    K : number;
    M : number;
    d : number;
    algorithm : Algorithm;
    algorithm_synchronization : string;
    algorithm_security : string;
    iteration : string;
}
