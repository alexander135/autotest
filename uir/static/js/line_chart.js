Chart.defaults.global.responsive = false;

var ctx = document.getElementById("LineChart")

var LineChart = new Chart(ctx, {
    type: 'line',
    data: chartData,
    })
