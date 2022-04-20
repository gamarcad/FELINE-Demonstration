import {EChartsOption} from "echarts";

export interface NGXLinearLine {
    name : string,
    y : number[],
    x : number[],
}

export interface NGXLinearSerie {
    line_name : string,
    y_name : string,
    x_name : string,
    title? : string,
    legend? : boolean,
    lines : NGXLinearLine[],
}

export class NGXLinearPlot {

  static Empty() : EChartsOption {
      return {
          title: {
              text: ''
          },
          toolbox: {
              show: true,
          },
          xAxis: {
              boundaryGap: false,
              data: []
          },
          yAxis: {
              type: 'value',
          },
          series: []
      };

  }

  static CreateMultiLinesOptions( serie : NGXLinearSerie  ) : EChartsOption {
      // prepare data
      let data : any = []
      serie.lines.forEach( line => {
          data.push({
              name: line.name,
              type: 'line',
              data: line.y,
              markLine: {
                  //data: [{ type: 'average', name: 'Avg' }]
              }
          })
      } )

      // search for x
      let x = serie.lines[0].x

      return  {
          title: {
              text: serie.title ? serie.title : "",
          },
          tooltip: {
              trigger: 'axis'
          },
          legend: {
              show: !!serie.legend,
              align: 'left',
              bottom: "0%",
          },
          toolbox: {
              show: true,
              feature: {
                  dataZoom: {
                      yAxisIndex: 'none'
                  },
                  magicType: { type: ['line', 'bar'] },
              }
          },
          xAxis: {
              boundaryGap: false,
              data: x,
              name: serie.x_name,
              position: "bottom",
              nameLocation: "middle",
              nameGap: 20,
          },
          yAxis: {
              type: 'value',
              name: serie.y_name,
          },
          series: data
      };
  }
}
