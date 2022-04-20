import {EChartsOption} from "echarts";


export interface NGXBar {
    name : string,
    x : string[],
    y : number[]
}

export interface NGXBarSerie {
    y_name : string,
    y_max? : number,
    title? : string,
    bars : NGXBar[],
}

export class NGXBarPlot {
    static CreateBarOption() : EChartsOption {
        return {
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'shadow'
                }
            },
            legend: {
                data: ['Unsecure', 'Secure']
            },
            toolbox: {
                show: true,
                feature: {
                    mark: { show: true },
                    dataView: { show: true, readOnly: false },
                    magicType: { show: true, type: ['line', 'bar', 'stack'] },
                    restore: { show: true },
                    saveAsImage: { show: true }
                }
            },
            xAxis: [
                {
                    type: 'category',
                    axisTick: { show: false },
                    data: ['DO1', 'DO2', 'Server']
                }
            ],
            yAxis: [
                {
                    type: 'value'
                }
            ],
            series: [
                {
                    name: 'Unsecure',
                    type: 'bar',
                    emphasis: {
                        focus: 'series'
                    },
                    data: [220, 182, 1000, 234, 290]
                },
                {
                    name: 'Secure',
                    type: 'bar',
                    barGap: 0,
                    emphasis: {
                        focus: 'series'
                    },
                    data: [320, 332, 301, 334, 390]
                },


            ]
        };
    }


    static CreateMultiBarsOption( serie : NGXBarSerie ) : EChartsOption {
        // define the x
        let x = serie.bars[0].x

        // define the list of bars names
        let names : string[] = []
        serie.bars.forEach( bar => {
            names.push(bar.name)
        } )

        // define data
        let data : any = []
        serie.bars.forEach( bar => {
            data.push({
                name: bar.name,
                type: 'bar',
                barGap: 0,
                emphasis: {
                    focus: 'series'
                },
                data: bar.y
            })
        } )

        return {
            title: {
              text: serie.title ? serie.title : "",
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'shadow'
                }
            },
            legend: {
                show: true,
                type: 'plain',
                align: 'left',
                bottom: '0%',
                data: names
            },
            toolbox: {
                show: true,
                feature: {
                    mark: { show: true },
                    dataView: { show: true, readOnly: false },
                    magicType: { show: true, type: ['line', 'bar', 'stack'] },
                }
            },
            xAxis: [
                {
                    type: 'category',
                    axisTick: { show: false },
                    data: x,
                }
            ],
            yAxis: [
                {
                    name: serie.y_name,
                    type: 'value',
                    max: serie.y_max,
                },
            ],
            series: data
        };
    }
}
