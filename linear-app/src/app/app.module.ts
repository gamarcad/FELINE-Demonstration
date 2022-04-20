import {NgModule} from '@angular/core';
import {BrowserModule} from '@angular/platform-browser';

import {AppRoutingModule} from './app-routing.module';
import {AppComponent} from './app.component';
import {ProtocolAnalysisComponent} from './protocol-analysis/protocol-analysis.component';
import {ParametersImpactComponent} from './parameters-impact/parameters-impact.component';
import {LikelihoodRetrieveComponent} from './likelihood-retrieve/likelihood-retrieve.component';
import {FormsModule} from "@angular/forms";
import {NgxEchartsModule} from "ngx-echarts";
import {HttpClientModule} from '@angular/common/http';

@NgModule({
    declarations: [
        AppComponent,
        ProtocolAnalysisComponent,
        ParametersImpactComponent,
        LikelihoodRetrieveComponent
    ],
    imports: [
        HttpClientModule,
        BrowserModule,
        AppRoutingModule,
        FormsModule,
        NgxEchartsModule.forRoot({
            echarts: () => import('echarts')
        })
    ],
    providers: [],
    bootstrap: [AppComponent]
})
export class AppModule {
}
