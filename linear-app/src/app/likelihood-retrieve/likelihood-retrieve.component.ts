import { Component, OnInit } from '@angular/core';
import {EChartsOption} from "echarts";
import {NGXBarPlot} from "../global/ngx-echarts/bar";

@Component({
    selector: 'app-likelihood-retrieve',
    templateUrl: './likelihood-retrieve.component.html',
    styleUrls: ['./likelihood-retrieve.component.scss', '../global/bar.scss']
})
export class LikelihoodRetrieveComponent implements OnInit {

    public unsecureOptions : EChartsOption = NGXBarPlot.CreateBarOption();
    public secureOptions : EChartsOption = NGXBarPlot.CreateBarOption();

    ngOnInit(): void {
    }

}
