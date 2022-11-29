import {Component, OnInit} from '@angular/core';
import {NGXLinearLine, NGXLinearPlot, NGXLinearSerie} from "../global/ngx-echarts/linear";
import {EChartsOption} from "echarts";
import {NGXBarPlot} from "../global/ngx-echarts/bar";
import {BackEnd} from "../api/BackEnd";
import {Algorithm} from "../entities/Algorithm";
import {AlgorithmSecurity, securityMethods} from "../entities/AlgorithmSecurity";
import {AlgorithmSynchronization, synchronizationMethods} from "../entities/AlgorithmSynchronization";
import {CumulativeExecutionTimeBySynchronization} from "../api/response/CumulativeExecutionTimeBySynchronization";
import {ThethaMSEBySynchronization} from "../api/response/ThethaMSEBySynchronization";
import {ParametersValues} from "../api/response/ParametersValues";
import {ComponentExecutionTimeBySynchronization} from "../api/response/ComponentExecutionTimeBySynchronization";
import {ComponentExecutionTime} from "../api/response/ComponentExecutionTime";
import {RewardsBySynchronization} from "../api/response/RewardsBySynchronization";

// Interface containing inputs from user
interface UserInputs {
    security: AlgorithmSecurity;
    synchronization : AlgorithmSynchronization;
    M : number;
    N : number;
    K : number;
    d : number;
}


@Component({
    selector: 'app-protocol-analysis',
    templateUrl: './protocol-analysis.component.html',
    styleUrls: ['./protocol-analysis.component.scss', '../global/bar.scss']
})
export class ProtocolAnalysisComponent implements OnInit {

    /* Possible parameters values */
    public parametersValues : ParametersValues = ProtocolAnalysisComponent.EmptyParametersValues();

    /* For the access from the HTML */
    public PLAINTEXT_VERSION = AlgorithmSecurity.PLAINTEXT
    public MASKED_VERSION = AlgorithmSecurity.MASKED

    /* User inputs */
    public userInputs : UserInputs = {
        M: 0,
        N: 0,
        K: 0,
        d: 0,
        security: AlgorithmSecurity.PLAINTEXT,
        synchronization: AlgorithmSynchronization.NO_SYNC,
    }

    /* Access to the list of security from the html */
    public possibleSecurities = securityMethods

    /* Access to the list of synchronization from the html */
    public possibleSynchronizations = synchronizationMethods

    /**
     * Handles the event when the user has modified some inputs.
     */
    public inputChangedByUser() {
        this.updateDiagrams()
    }




    /* Federated - Rewards */
    public federatedRewardsOption : EChartsOption = NGXLinearPlot.Empty()

    /* Federated - MSE */
    public federatedMSEOption : EChartsOption = NGXLinearPlot.Empty()

    /* Security - Plaintext Time By Components */
    public securityPlaintextTimeByComponentOption : EChartsOption = NGXBarPlot.CreateBarOption();

    /* Security - Masked Time By Components */
    public securityMaskedTimeByComponentOption : EChartsOption = NGXBarPlot.CreateBarOption();

    /* Scalability - Time by M */
    public scalabilityTimeByMParamOption : EChartsOption = NGXLinearPlot.Empty();

    /* Scalability - Time by d */
    public scalabilityTimeBydParamOption : EChartsOption = NGXLinearPlot.Empty();

    /* Scalability - Time by K */
    public scalabilityTimeByKParamOption : EChartsOption = NGXLinearPlot.Empty();

    /* Scalability - Time by N */
    public scalabilityTimeByNParamOption : EChartsOption = NGXLinearPlot.Empty();


    constructor( public backend : BackEnd ) {
    }

    ngOnInit(): void {
        this.backend.getParametersValues().subscribe(parameters => {
            // update the user inputs from the received parameters
            this.parametersValues = parameters;
            this.userInputs.d = parameters.list_d[0]
            this.userInputs.M = parameters.list_M[0]
            this.userInputs.N = parameters.list_N[0]
            this.userInputs.K = parameters.list_K[0]

            console.log(this.userInputs)
            this.updateDiagrams();
        })
    }


    private updateDiagrams() {
        /*
        this.backend.getCumulativeExecutionTimeBySynchronization({
            algorithm: Algorithm.LINUCB,
            algorithm_security:  this.userInputs.security,
            M: this.userInputs.M,
            N: this.userInputs.N,
            d: this.userInputs.d,
            K: this.userInputs.K,
            iteration: 'it-0',
        }).subscribe(
            ( executionTimeByTurn:  CumulativeExecutionTimeBySynchronization ) => {

                this.securityTimeOption = NGXLinearPlot.CreateMultiLinesOptions({
                    title: "Total Time",
                    legend: true,
                    x_name: "Time Step",
                    y_name: "Time (s)",
                    line_name: "Execution Time by Sync",
                    lines: [
                        {
                            name: AlgorithmSynchronization.NO_SYNC,
                            x: executionTimeByTurn["no-sync"].turns,
                            y: executionTimeByTurn["no-sync"].times
                        },
                        {
                            name: AlgorithmSynchronization.FOUR_STEPS,
                            x: executionTimeByTurn["four-steps"].turns,
                            y: executionTimeByTurn["four-steps"].times
                        },
                        {
                            name: AlgorithmSynchronization.TWO_STEPS,
                            x: executionTimeByTurn["two-steps"].turns,
                            y: executionTimeByTurn["two-steps"].times
                        },
                        {
                            name: AlgorithmSynchronization.EACH_STEP,
                            x: executionTimeByTurn["each-step"].turns,
                            y: executionTimeByTurn["each-step"].times
                        },
                    ]
                })
            }
        )
        */

        this.backend.getRewardsBySynchronization({
            algorithm: Algorithm.LINUCB,
            algorithm_security: this.userInputs.security,
            M: this.userInputs.M,
            N: this.userInputs.N,
            d: this.userInputs.d,
            K: this.userInputs.K,
        }).subscribe(
            ( response:  RewardsBySynchronization ) => {
                this.federatedRewardsOption = NGXLinearPlot.CreateMultiLinesOptions({
                    title: "Rewards by Synchronization",
                    legend: true,
                    x_name: "Time Step",
                    y_name: "Rewards",
                    line_name: "",
                    lines: [
                        {
                            name: AlgorithmSynchronization.NO_SYNC,
                            x: response.turns,
                            y: response["no-sync"].rewards
                        },
                        {
                            name: AlgorithmSynchronization.FOUR_STEPS,
                            x: response.turns,
                            y: response["four-steps"].rewards
                        },
                        {
                            name: AlgorithmSynchronization.TWO_STEPS,
                            x: response.turns,
                            y: response["two-steps"].rewards
                        },
                        {
                            name: AlgorithmSynchronization.EACH_STEP,
                            x: response.turns,
                            y: response["each-step"].rewards
                        },

                    ]
                })
            }
        )




        this.backend.getComponentExecutionTimeBySynchronization({
            algorithm: Algorithm.LINUCB,
            algorithm_security: AlgorithmSecurity.PLAINTEXT,
            M: this.userInputs.M,
            N: this.userInputs.N,
            d: this.userInputs.d,
            K: this.userInputs.K,
        }).subscribe(
            ( data : ComponentExecutionTimeBySynchronization ) => {

                // calls the API for the masked version
                this.backend.getComponentExecutionTimeBySynchronization({
                    algorithm: Algorithm.LINUCB,
                    algorithm_security: AlgorithmSecurity.MASKED,
                    M: this.userInputs.M,
                    N: this.userInputs.N,
                    d: this.userInputs.d,
                    K: this.userInputs.K,
                }).subscribe(
                    ( data2 : ComponentExecutionTimeBySynchronization ) => {
                        // compute the max execution time in order to adjust the plot
                        let plaintextMaxExecutionTime = this.maxExecutionTime( data );
                        let maskedMaxExecutionTime = this.maxExecutionTime( data2 );
                        let maxExecutionTime = plaintextMaxExecutionTime < maskedMaxExecutionTime ? maskedMaxExecutionTime : plaintextMaxExecutionTime
                        maxExecutionTime = Number(maxExecutionTime.toFixed(1)) ;

                        // plot the plaintext version
                        this.securityPlaintextTimeByComponentOption = NGXBarPlot.CreateMultiBarsOption({
                            title: "Participant Time (Plaintext)",
                            y_name: "Time (s)",
                            y_max: maxExecutionTime,
                            bars:  [
                                {
                                    name: AlgorithmSynchronization.NO_SYNC,
                                    x: data.entities,
                                    y: data["no-sync"].times,
                                },
                                {
                                    name: AlgorithmSynchronization.FOUR_STEPS,
                                    x: data.entities,
                                    y: data["four-steps"].times,
                                },
                                {
                                    name: AlgorithmSynchronization.TWO_STEPS,
                                    x: data.entities,
                                    y: data["two-steps"].times,
                                },
                                {
                                    name: AlgorithmSynchronization.EACH_STEP,
                                    x: data.entities,
                                    y: data["each-step"].times,
                                },
                            ]
                        })


                        // plit the masked version
                        this.securityMaskedTimeByComponentOption = NGXBarPlot.CreateMultiBarsOption({
                            title: "Participant Time (Ciphertext)",
                            y_name: "Time (s)",
                            y_max: maxExecutionTime,
                            bars:  [
                                {
                                    name: AlgorithmSynchronization.NO_SYNC,
                                    x: data2.entities,
                                    y: data2["no-sync"].times,
                                },
                                {
                                    name: AlgorithmSynchronization.FOUR_STEPS,
                                    x: data2.entities,
                                    y: data2["four-steps"].times,
                                },
                                {
                                    name: AlgorithmSynchronization.TWO_STEPS,
                                    x: data2.entities,
                                    y: data2["two-steps"].times,
                                },
                                {
                                    name: AlgorithmSynchronization.EACH_STEP,
                                    x: data2.entities,
                                    y: data2["each-step"].times,
                                },
                            ]
                        })
                    }
                );


            }
        )

        this.backend.getTimeWhenVaryingParamK({
            algorithm: Algorithm.LINUCB,
            algorithm_security: this.userInputs.security,
            N: this.userInputs.N,
            M: this.userInputs.M,
            d: this.userInputs.d,

        }).subscribe( response => {

            this.scalabilityTimeByKParamOption = NGXLinearPlot.CreateMultiLinesOptions({
                title: "Variation of K",
                x_name: "K",
                y_name: "Time (s)",
                line_name: "Rewards by K",
                lines: [
                    {
                        name: AlgorithmSynchronization.NO_SYNC,
                        x: response["no-sync"].param_values,
                        y: response["no-sync"].times
                    },
                    {
                        name: AlgorithmSynchronization.FOUR_STEPS,
                        x: response["four-steps"].param_values,
                        y: response["four-steps"].times
                    },
                    {
                        name: AlgorithmSynchronization.TWO_STEPS,
                        x: response["two-steps"].param_values,
                        y: response["two-steps"].times
                    },
                    {
                        name: AlgorithmSynchronization.EACH_STEP,
                        x: response["each-step"].param_values,
                        y: response["each-step"].times
                    },
                ]
            })
        } )

        this.backend.getTimeWhenVaryingParamM({
            algorithm: Algorithm.LINUCB,
            algorithm_security: this.userInputs.security,
            N: this.userInputs.N,
            K: this.userInputs.K,
            d: this.userInputs.d,

        }).subscribe( response => {
            this.scalabilityTimeByMParamOption = NGXLinearPlot.CreateMultiLinesOptions({
                title: "Variation of M",
                x_name: "M",
                y_name: "Time (s)",
                line_name: "Rewards by M",
                lines: [
                    {
                        name: AlgorithmSynchronization.NO_SYNC,
                        x: response["no-sync"].param_values,
                        y: response["no-sync"].times
                    },
                    {
                        name: AlgorithmSynchronization.FOUR_STEPS,
                        x: response["four-steps"].param_values,
                        y: response["four-steps"].times
                    },
                    {
                        name: AlgorithmSynchronization.TWO_STEPS,
                        x: response["two-steps"].param_values,
                        y: response["two-steps"].times
                    },
                    {
                        name: AlgorithmSynchronization.EACH_STEP,
                        x: response["each-step"].param_values,
                        y: response["each-step"].times
                    },
                ]
            })
        } )

        this.backend.getTimeWhenVaryingParamN({
            algorithm: Algorithm.LINUCB,
            algorithm_security: this.userInputs.security,
            M: this.userInputs.M,
            K: this.userInputs.K,
            d: this.userInputs.d,

        }).subscribe( response => {
            this.scalabilityTimeByNParamOption = NGXLinearPlot.CreateMultiLinesOptions({
                title: "Variation of N",
                x_name: "N",
                y_name: "Time (s)",
                line_name: "Times by N",
                lines: [
                    {
                        name: AlgorithmSynchronization.NO_SYNC,
                        x: response["no-sync"].param_values,
                        y: response["no-sync"].times
                    },
                    {
                        name: AlgorithmSynchronization.FOUR_STEPS,
                        x: response["four-steps"].param_values,
                        y: response["four-steps"].times
                    },
                    {
                        name: AlgorithmSynchronization.TWO_STEPS,
                        x: response["two-steps"].param_values,
                        y: response["two-steps"].times
                    },
                    {
                        name: AlgorithmSynchronization.EACH_STEP,
                        x: response["each-step"].param_values,
                        y: response["each-step"].times
                    },
                ]
            })
        } )


        this.backend.getTimeWhenVaryingParamd({
            algorithm: Algorithm.LINUCB,
            algorithm_security: this.userInputs.security,
            N: this.userInputs.N,
            K: this.userInputs.K,
            M: this.userInputs.M,
        }).subscribe( response => {
            this.scalabilityTimeBydParamOption = NGXLinearPlot.CreateMultiLinesOptions({
                title: "Variation of d",
                x_name: "d",
                y_name: "Time (s)",
                line_name: "Rewards by d",
                lines: [
                    {
                        name: AlgorithmSynchronization.NO_SYNC,
                        x: response["no-sync"].param_values,
                        y: response["no-sync"].times
                    },
                    {
                        name: AlgorithmSynchronization.FOUR_STEPS,
                        x: response["four-steps"].param_values,
                        y: response["four-steps"].times
                    },
                    {
                        name: AlgorithmSynchronization.TWO_STEPS,
                        x: response["two-steps"].param_values,
                        y: response["two-steps"].times
                    },
                    {
                        name: AlgorithmSynchronization.EACH_STEP,
                        x: response["each-step"].param_values,
                        y: response["each-step"].times
                    },
                ]
            })
        } )



        this.federatedMSEOption = NGXLinearPlot.CreateMultiLinesOptions(
            this.generateCumulativeCommunicationsCostLine()
        )
    }


    private generateCumulativeCommunicationsCostLine() : NGXLinearSerie {
        // define the number of bits required to represent a float
        const BITS_FOR_FLOAT = 64;
        let synchronizationMessageBits = this.userInputs.d * BITS_FOR_FLOAT + this.userInputs.d * this.userInputs.d * BITS_FOR_FLOAT



        // the communications cost consists of an estimation of the number of bits
        // coming through the network, depending on the synchronization strategy and the cryptography.
        let lines : NGXLinearLine[] = [];
        for ( let synchronization of synchronizationMethods ) {
            let turns = []
            let cumulativeNumberOfKiloBits: number[] = []
            let currentNumberOfBits = 0
            for (let turn = 1; turn < this.userInputs.N; turn++) {
                turns.push(turn)

                // check if a synchronization has been required
                let hasSynchronized =
                    (synchronization == AlgorithmSynchronization.EACH_STEP) ||
                    (synchronization == AlgorithmSynchronization.TWO_STEPS && turn % 2 == 0) ||
                    (synchronization == AlgorithmSynchronization.FOUR_STEPS && turn % 4 == 0)
                ;

                // compute the number of bits
                if (hasSynchronized) {
                    currentNumberOfBits += synchronizationMessageBits;
                }

                cumulativeNumberOfKiloBits.push( currentNumberOfBits / 1000 )

            }

            // store the result
            lines.push({
                name: synchronization,
                x: turns,
                y: cumulativeNumberOfKiloBits
            })
        }

        // returns the serie
        return {
            title: "Communications Cost",
            legend: true,
            x_name: "Time Step",
            y_name: "KB",
            line_name: "Number of bits",
            lines: lines
        }
    }

    private static EmptyParametersValues() : ParametersValues {
        return {
            list_K: [], list_M: [], list_N: [], list_d: []
        }
    }

    private maxExecutionTime( data : ComponentExecutionTimeBySynchronization ) : number {
        // As execution time is positive or zero, the initial execution time can be zero
        let maxExecutionTimeBySynchronization = [
            this.maxExecutionTimeForComponentExecutionTime( data["each-step"] ),
            this.maxExecutionTimeForComponentExecutionTime( data["no-sync"] ),
            this.maxExecutionTimeForComponentExecutionTime( data["two-steps"] ),
            this.maxExecutionTimeForComponentExecutionTime( data["four-steps"] ),
        ]

        return maxExecutionTimeBySynchronization.reduce(
            (previousValue, currentValue) => previousValue < currentValue ? currentValue : previousValue
        )
    }

    private maxExecutionTimeForComponentExecutionTime( componentExecutionTime : ComponentExecutionTime ) {
        return componentExecutionTime.times.reduce(
            (previousValue, currentValue) => previousValue < currentValue ? currentValue : previousValue
        )
    }

    setUserInputSecurity( algorithm_security: AlgorithmSecurity) {
        this.userInputs.security = algorithm_security
        this.updateDiagrams()
    }
}
