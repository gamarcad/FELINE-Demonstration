import {Rewards} from "./Rewards";

export interface RewardsBySynchronization {
    "no-sync": Rewards,
    "four-steps" : Rewards,
    "two-steps" : Rewards,
    "each-step" : Rewards,
    "turns": number[],
}
