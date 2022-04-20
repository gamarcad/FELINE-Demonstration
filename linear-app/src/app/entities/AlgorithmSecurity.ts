export enum AlgorithmSecurity {
    PLAINTEXT = "plaintext-version",
    MASKED = "masked-version",
}

export const securityMethods = [
    AlgorithmSecurity.PLAINTEXT,
    AlgorithmSecurity.MASKED,
]
