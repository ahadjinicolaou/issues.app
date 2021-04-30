const ISSUE_STATUS_COLORS = {
    'NEW': '#8ACDEA',
    'ASSIGNED': '#586BA4',
    'ACCEPTED': '#324376',
    'FIXED': '#F1D302',
    'RESOLVED': '#161925',
    'DISMISSED': '#555555',
}

const PROJECT_STATUS_COLORS = {
    'NEW': '#8ACDEA',
    'ACTIVE': '#586BA4',
    'INACTIVE': '#CCCCCC'
};

const DOUGHNUT_OPTIONS = {
    legend: {
        display: false,
        position: 'right',
    },
    plugins: {
        datalabels: {
            display: true,
            formatter: (val, ctx) => {
                return ctx.chart.data.labels[ctx.dataIndex];
            },
            color: '#fff',
        },
    }
};

const STACKED_BAR_OPTIONS = {
    legend: {
        display: true,
        position: 'bottom',
    },
    tooltips: {
        enabled: false
    },
    hover: {
        mode: null
    },
    scales: {
        xAxes: [{
            ticks: {
                beginAtZero: true,
            },
            scaleLabel: {
                display: false
            },
            stacked: true,
        }],
        yAxes: [{
            stacked: true,
        }],
    },
    plugins: {
        datalabels: {
            display: false,
        },
    }
};

function plotBarChart(canvasId, data, isHorizontal = true) {
    var ctx = document.getElementById(canvasId).getContext('2d');
    var chart = new Chart(ctx, {
        type: isHorizontal ? 'horizontalBar' : 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
            }],
        },
        options: STACKED_BAR_OPTIONS,
    });
}

function plotStackedBarChart(canvasId, data, labels, colors, isHorizontal = true) {
    const datasets = data.map(function (val, idx) {
        return {
            'data': [data[idx]],
            'label': labels[idx],
            'backgroundColor': colors[idx]
        };
    });

    var ctx = document.getElementById(canvasId).getContext('2d');
    var chart = new Chart(ctx, {
        type: isHorizontal ? 'horizontalBar' : 'bar',
        data: {
            datasets: datasets
        },
        options: STACKED_BAR_OPTIONS
    });
}

function plotDoughnutChart(canvasId, data, labels, colors) {
    var ctx = document.getElementById(canvasId).getContext('2d');
    var chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
            }]
        },
        options: DOUGHNUT_OPTIONS,
    });
}