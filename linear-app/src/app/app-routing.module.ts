import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import {ProtocolAnalysisComponent} from "./protocol-analysis/protocol-analysis.component";
import {ParametersImpactComponent} from "./parameters-impact/parameters-impact.component";
import {LikelihoodRetrieveComponent} from "./likelihood-retrieve/likelihood-retrieve.component";

const routes: Routes = [
  {
    path: "",
    component: ProtocolAnalysisComponent,
  },
  {
    path: "parameters",
    component: ParametersImpactComponent,
  },
  {
    path: "security",
    component: LikelihoodRetrieveComponent,
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
