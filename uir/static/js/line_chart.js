Chart.defaults.global.responsive = true;
Chart.defaults.global.maintainAspectRatio = false;
Chart.defaults.global.aspectRatio = 5;
var ctx = document.getElementById("LineChart")
var chartData = {
    labels : chart_data['date'],
    datasets: [{
        label : 'Failed',
        lineTension: 0.1,
        backgroundColor: "rgba(220, 53, 69,0.5)",
        fill: true,
        data: chart_data['failed']
        },
        {
        label : 'Skipped',
        lineTension: 0.1,
        backgroundColor: "rgba(255, 193, 7, 0.5)",
        fill: true,
        data: chart_data['skipped']
        },
        {
        label : 'Passed',
        lineTension: 0.1,
        backgroundColor: "rgba(40, 167, 69,0.5)",
        fill: true,
        data: chart_data['passed'],
    },

]
}
var LineChart = new Chart(ctx, {
    type: 'line',
    data: chartData,
    options: {
        legend: {
                display: true,
        onClick :
            function(e, legendItem) {
                            var index = legendItem.datasetIndex;
                                        var ci = this.chart;
                                                    var meta = ci.getDatasetMeta(index);

                             meta.hidden = meta.hidden === null ? 
                             !ci.data.datasets[index].hidden : null;
                             ci.update();
            }                                                              
        }, 
        title: {
            display: true,
            text: Name,
            },
            onClick:
                function(evt, item){
                    try{
                        console.log(evt,item[0]['_index'], item);
                    pk = item[0]['_chart']['config']['data']['labels'][item[0]['_index']][1];
                    if (pk >= 0){
                        location.href = pk
                            }
                        }
                    catch(err){
                    }
                     },
            hover:{
                mode: 'nearest',
                intersect: true
                }, 
            tooltips:{
                mode: 'index',
                intersect: false,
                },
            scales:{
                yAxes:[{
                    stacked:true,
                }]
            }
        }
    })
LineChart.canvas.parentNode.style.height = '21vw';
LineChart.canvas.parentNode.style.width = '70vw';
