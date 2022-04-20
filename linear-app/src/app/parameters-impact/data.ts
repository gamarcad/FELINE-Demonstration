import {ParametersImpactEntry} from "./parameters-impact.component";

export class ParametersImpactData {
    public static GetData() : ParametersImpactEntry[] {
        let data : ParametersImpactEntry[] = []
        for ( let index = 1; index < 200; index++ ) {
            data.push({
                M: 1,
                N: 2,
                K: 1,
                d: 1,
                sync: true,
                sec: true,
                time: 20,
                rewards: 200
            })
        }
        return data
    }
}