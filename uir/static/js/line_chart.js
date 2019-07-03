Chart.defaults.global.responsive = false;

var ctx = document.getElementById("LineChart")

var chartData = {
    labels : chart_data['date'],
    datasets: [{
        label : 'Passed',
        lineTension: 0.1,
        backgroundColor: "rgba(40, 167, 69,0.5)",
        fill: true,
        data: chart_data['passed'],
    },
        {
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
        }

]
}
var LineChart = new Chart(ctx, {
    type: 'line',
    data: chartData,
    options: {
        title: {
            display: true,
            text: Name,
            },
            onClick:
                function(evt, item){
                    console.log(evt,item[0]['_index'], item);
                    pk = item[0]['_chart']['config']['data']['labels'][item[0]['_index']][1];
                    if (pk >= 0){
                        location.href = pk
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
        }
    })
