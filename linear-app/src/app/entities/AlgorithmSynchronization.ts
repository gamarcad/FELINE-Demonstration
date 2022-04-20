export enum AlgorithmSynchronization {
    NO_SYNC = "no-aggreg",
    EACH_STEP = "each-step",
    TWO_STEPS = "two-steps",
    FOUR_STEPS = "four-steps"
}

export const synchronizationMethods = [
    AlgorithmSynchronization.NO_SYNC,
    AlgorithmSynchronization.FOUR_STEPS,
    AlgorithmSynchronization.TWO_STEPS,
    AlgorithmSynchronization.EACH_STEP,
]
