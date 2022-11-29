import {HttpClient, HttpErrorResponse} from "@angular/common/http";
import {environment} from "../../environments/environment";
import {ConfigurationBodyRequest} from "./request/ConfigurationBodyRequest";
import {Injectable} from "@angular/core";
import {Observable, throwError} from "rxjs";
import {catchError, retry} from "rxjs/operators";
import {CumulativeExecutionTime} from "./response/CumulativeExecutionTime";
import {CumulativeExecutionTimeBySynchronization} from "./response/CumulativeExecutionTimeBySynchronization";
import {
    CumulativeExecutionTimeBySynchronizationRequest
} from "./request/CumulativeExecutionTimeBySynchronizationRequest";
import {ThetaMSEBySynchronizationRequest} from "./request/ThetaMSEBySynchronizationRequest";
import {ThethaMSEBySynchronization} from "./response/ThethaMSEBySynchronization";
import {ComponentExecutionTimeBySecurity} from "./response/ComponentExecutionTimeBySecurity";
import {ComponentExecutionTimeBySecurityRequest} from "./request/ComponentExecutionTimeBySecurityRequest";
import {TimeWhenVaryingParamKRequest} from "./request/TimeWhenVaryingParamKRequest";
import {TimeWhenVaryingParamNRequest} from "./request/TimeWhenVaryingParamNRequest";
import {TimeWhenVaryingParamMRequest} from "./request/TimeWhenVaryingParamMRequest";
import {TimeWhenVaryingParamdRequest} from "./request/TimeWhenVaryingParamdRequest";
import {TimeWhileVaryingParameterBySynchronization} from "./response/TimeWhileVaryingParameterBySynchronization";
import {ParametersValues} from "./response/ParametersValues";
import {ComponentExecutionTimeBySynchronization} from "./response/ComponentExecutionTimeBySynchronization";
import {ComponentExecutionTimeBySynchronizationRequest} from "./request/ComponentExecutionTimeBySynchronizationRequest";
import {RewardsBySynchronization} from "./response/RewardsBySynchronization";
import {RewardsBySynchronizationRequest} from "./request/RewardsBySynchronizationRequest";

@Injectable({
    providedIn: 'root'
})
export class BackEnd {
    private static CUMULATIVE_EXECUTION_TIME_BY_SYNC : string  = "/cumulative-execution-time/sync";
    private static THETA_MSE_BY_SYNC : string  = "/theta-mse/sync";
    private static COMPONENT_EXECUTION_TIME_BY_SECURITY : string  = "/component-execution-time/security";
    private static COMPONENT_EXECUTION_TIME_BY_SYNCHRONIZATION : string  = "/component-execution-time/synchronization";
    private static TIME_WHEN_VARYING_K : string  = "/times/K";
    private static TIME_WHEN_VARYING_M : string  = "/times/M";
    private static TIME_WHEN_VARYING_N : string  = "/times/N";
    private static TIME_WHEN_VARYING_d : string  = "/times/d";
    private static REWARDS_BY_SYNC : string  = "/rewards/sync";
    private static PARAMETERS_VALUES : string = "/parameters/values"


    httpClient : HttpClient;
    endpoint : String;

    constructor( httpClient : HttpClient ) {
        this.httpClient = httpClient;
        this.endpoint = environment.endpoint;
    }

    getParametersValues() : Observable<ParametersValues> {
        return this.httpClient.get<ParametersValues>( this.endpoint + BackEnd.PARAMETERS_VALUES )
            .pipe(
                retry(1),
                catchError(this.processError)
            )
    }

    getComponentExecutionTimeBySecurity(configuration : ComponentExecutionTimeBySecurityRequest ) : Observable<ComponentExecutionTimeBySecurity> {
        return this.httpClient.get<ComponentExecutionTimeBySecurity>( this.endpoint + BackEnd.COMPONENT_EXECUTION_TIME_BY_SECURITY, {
            params: {
                N: configuration.N,
                M: configuration.M,
                K: configuration.K,
                d: configuration.d,
                algorithm: configuration.algorithm,
                algorithm_synchronization: configuration.algorithm_synchronization,
                iteration: configuration.iteration,
            }
        }).pipe(
            retry(1),
            catchError(this.processError)
        );
    }

    getComponentExecutionTimeBySynchronization(configuration : ComponentExecutionTimeBySynchronizationRequest ) : Observable<ComponentExecutionTimeBySynchronization> {
        return this.httpClient.get<ComponentExecutionTimeBySynchronization>( this.endpoint + BackEnd.COMPONENT_EXECUTION_TIME_BY_SYNCHRONIZATION, {
            params: {
                N: configuration.N,
                M: configuration.M,
                K: configuration.K,
                d: configuration.d,
                algorithm: configuration.algorithm,
                algorithm_security: configuration.algorithm_security,
            }
        }).pipe(
            retry(1),
            catchError(this.processError)
        );
    }

    getCumulativeExecutionTimeBySynchronization(configuration : CumulativeExecutionTimeBySynchronizationRequest ) : Observable<CumulativeExecutionTimeBySynchronization> {
        return this.httpClient.get<CumulativeExecutionTimeBySynchronization>( this.endpoint + BackEnd.CUMULATIVE_EXECUTION_TIME_BY_SYNC, {
            params: {
                N: configuration.N,
                M: configuration.M,
                K: configuration.K,
                d: configuration.d,
                algorithm: configuration.algorithm,
                algorithm_security: configuration.algorithm_security,
                iteration: configuration.iteration,
            }
        }).pipe(
            retry(1),
            catchError(this.processError)
        );
    }

    getThetaMSEBySynchronization(configuration : ThetaMSEBySynchronizationRequest ) : Observable<ThethaMSEBySynchronization> {
        return this.httpClient.get<ThethaMSEBySynchronization>( this.endpoint + BackEnd.THETA_MSE_BY_SYNC, {
            params: {
                N: configuration.N,
                M: configuration.M,
                K: configuration.K,
                d: configuration.d,
                algorithm: configuration.algorithm,
                algorithm_security: configuration.algorithm_security,
                iteration: configuration.iteration,
            }
        }).pipe(
            retry(1),
            catchError(this.processError)
        );
    }

    getTimeWhenVaryingParamK( configuration : TimeWhenVaryingParamKRequest ) : Observable<TimeWhileVaryingParameterBySynchronization> {
        return this.httpClient.get<TimeWhileVaryingParameterBySynchronization>( this.endpoint + BackEnd.TIME_WHEN_VARYING_K, {
            params: {
                N: configuration.N,
                M: configuration.M,
                d: configuration.d,
                algorithm: configuration.algorithm,
                algorithm_security: configuration.algorithm_security,
            }
        }).pipe(
            retry(1),
            catchError(this.processError)
        );
    }

    getTimeWhenVaryingParamM(configuration : TimeWhenVaryingParamMRequest ) : Observable<TimeWhileVaryingParameterBySynchronization> {
        return this.httpClient.get<TimeWhileVaryingParameterBySynchronization>( this.endpoint + BackEnd.TIME_WHEN_VARYING_M, {
            params: {
                N: configuration.N,
                K: configuration.K,
                d: configuration.d,
                algorithm: configuration.algorithm,
                algorithm_security: configuration.algorithm_security,
            }
        }).pipe(
            retry(1),
            catchError(this.processError)
        );
    }

    getTimeWhenVaryingParamN(configuration : TimeWhenVaryingParamNRequest ) : Observable<TimeWhileVaryingParameterBySynchronization> {
        return this.httpClient.get<TimeWhileVaryingParameterBySynchronization>( this.endpoint + BackEnd.TIME_WHEN_VARYING_N, {
            params: {
                M: configuration.M,
                K: configuration.K,
                d: configuration.d,
                algorithm: configuration.algorithm,
                algorithm_security: configuration.algorithm_security,
            }
        }).pipe(
            retry(1),
            catchError(this.processError)
        );
    }

    getTimeWhenVaryingParamd(configuration : TimeWhenVaryingParamdRequest ) : Observable<TimeWhileVaryingParameterBySynchronization> {
        return this.httpClient.get<TimeWhileVaryingParameterBySynchronization>( this.endpoint + BackEnd.TIME_WHEN_VARYING_d, {
            params: {
                M: configuration.M,
                K: configuration.K,
                N: configuration.N,
                algorithm: configuration.algorithm,
                algorithm_security: configuration.algorithm_security,
            }
        }).pipe(
            retry(1),
            catchError(this.processError)
        );
    }

    getRewardsBySynchronization(configuration : RewardsBySynchronizationRequest) : Observable<RewardsBySynchronization> {
        return this.httpClient.get<RewardsBySynchronization>( this.endpoint + BackEnd.REWARDS_BY_SYNC, {
            params: {
                N: configuration.N,
                M: configuration.M,
                K: configuration.K,
                d: configuration.d,
                algorithm: configuration.algorithm,
                algorithm_security: configuration.algorithm_security,
            }
        }).pipe(
            retry(1),
            catchError(this.processError)
        );
    }




    /**
     * Process HTTP Request errors.
     * @param err
     */
    processError(err : HttpErrorResponse) {
        let message = '';
        if(err.error instanceof ErrorEvent) {
            message = err.error.message;
        } else {
            message = `Error Code: ${err.status}\nMessage: ${err.message}`;
        }
        console.log(message);
        return throwError(message);
    }
}
