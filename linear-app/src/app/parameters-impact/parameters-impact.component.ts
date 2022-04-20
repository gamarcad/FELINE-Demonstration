import { Component, OnInit } from '@angular/core';
import {ParametersImpactData} from "./data";



export interface ParametersImpactEntry {
  M : number;
  N : number;
  K : number;
  d : number;
  sync : boolean;
  sec : boolean;

  rewards : number;
  time : number;
}

export interface ParametersImpactRow {
  entry : ParametersImpactEntry;
  show : boolean;
}

@Component({
  selector: 'app-parameters-impact',
  templateUrl: './parameters-impact.component.html',
  styleUrls: ['./parameters-impact.component.scss', "../global/bar.scss"]
})
export class ParametersImpactComponent implements OnInit {

  // exports the interface
  public parametersImpactRows :  ParametersImpactRow[] = function () : ParametersImpactRow[] {
    let entries : ParametersImpactEntry[] =  ParametersImpactData.GetData()
    return entries.map<ParametersImpactRow>((entry) => {
      return {
        entry: entry,
        show: true,
      }
    });
  }()

  public filter : string = "";

  ngOnInit(): void {
  }

}
