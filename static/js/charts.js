document.addEventListener('DOMContentLoaded', () => {
    if (typeof chartData === 'undefined' || !chartData.length) return;

    const periods = chartData.map(d => d.period);

    // 1. Выручка и чистая прибыль
    const revenueChart = echarts.init(document.getElementById('chart-revenue'));
    revenueChart.setOption({
        title: { text: 'Динамика выручки и прибыли', textStyle: { fontSize: 14 } },
        tooltip: { trigger: 'axis' },
        legend: { data: ['Выручка', 'Чистая прибыль'], bottom: 0 },
        grid: { left: 60, right: 20, top: 40, bottom: 50 },
        xAxis: { type: 'category', data: periods },
        yAxis: { type: 'value' },
        series: [
            { name: 'Выручка', type: 'line', smooth: true, data: chartData.map(d => d.revenue) },
            { name: 'Чистая прибыль', type: 'line', smooth: true, data: chartData.map(d => d.net_profit) }
        ]
    });

    // 2. Рентабельность: продажи и ROE
    const ratiosChart = echarts.init(document.getElementById('chart-ratios'));
    ratiosChart.setOption({
        title: { text: 'Показатели рентабельности', textStyle: { fontSize: 14 } },
        tooltip: { trigger: 'axis', valueFormatter: v => v != null ? v + '%' : '—' },
        legend: { data: ['Рентабельность продаж', 'ROE'], bottom: 0 },
        grid: { left: 60, right: 20, top: 40, bottom: 50 },
        xAxis: { type: 'category', data: periods },
        yAxis: { type: 'value', axisLabel: { formatter: '{value}%' } },
        series: [
            { name: 'Рентабельность продаж', type: 'bar', data: chartData.map(d => d.ratios.profitability ?? null) },
            { name: 'ROE', type: 'bar', data: chartData.map(d => d.ratios.roe ?? null) }
        ]
    });

    // 3. Индексы: Лернер и HHI
    const indexChart = echarts.init(document.getElementById('chart-indexes'));
    indexChart.setOption({
        title: { text: 'Индексы монопольной власти и концентрации', textStyle: { fontSize: 14 } },
        tooltip: {
            trigger: 'axis',
            valueFormatter: v => v != null ? v : '—'
        },
        legend: { data: ['Индекс Лернера', 'HHI'], bottom: 0 },
        grid: { left: 60, right: 60, top: 40, bottom: 50 },
        xAxis: { type: 'category', data: periods },
        yAxis: [
            { type: 'value', name: 'Лернер', min: 0, max: 1 },
            { type: 'value', name: 'HHI', min: 0, max: 10000 }
        ],
        series: [
            {
                name: 'Индекс Лернера',
                type: 'line',
                smooth: true,
                yAxisIndex: 0,
                data: chartData.map(d => d.ratios.lerner ?? null)
            },
            {
                name: 'HHI',
                type: 'line',
                smooth: true,
                yAxisIndex: 1,
                data: chartData.map(d => d.hhi ?? null)
            }
        ]
    });

    // 4. Radar — комплексная оценка с цифрами при наведении
    const last = chartData[chartData.length - 1];
    const radarChart = echarts.init(document.getElementById('chart-radar'));
    radarChart.setOption({
        title: { text: 'Комплексная оценка (' + last.period + ')', textStyle: { fontSize: 14 } },
        tooltip: {
            trigger: 'item',
            formatter: function (params) {
                const values = params.value;
                const names = [
                    'Рентабельность продаж',
                    'ROE',
                    'Автономия',
                    'Долговая нагрузка',
                    'Лернер'
                ];
                let html = '<b>' + params.name + '</b><br/>';
                for (let i = 0; i < names.length; i++) {
                    const v = values[i] != null ? values[i] : '—';
                    html += names[i] + ': ' + v + '<br/>';
                }
                return html;
            }
        },
        radar: {
            indicator: [
                { name: 'Рентабельность продаж', max: 50 },
                { name: 'ROE', max: 50 },
                { name: 'Автономия', max: 1 },
                { name: 'Долговая нагрузка', max: 5 },
                { name: 'Лернер', max: 1 }
            ],
            radius: '65%'
        },
        series: [{
            type: 'radar',
            data: [{
                value: [
                    last.ratios.profitability ?? 0,
                    last.ratios.roe ?? 0,
                    last.ratios.autonomy ?? 0,
                    last.ratios.debt_load ?? 0,
                    last.ratios.lerner ?? 0
                ],
                name: last.period,
                areaStyle: { opacity: 0.2 }
            }]
        }]
    });

    // 5. Круговая диаграмма доли рынка
    if (typeof marketShares !== 'undefined' && marketShares.length) {
        const shareEl = document.getElementById('chart-market-share');
        if (shareEl) {
            const shareChart = echarts.init(shareEl);
            shareChart.setOption({
                title: { text: 'Доля рынка по отрасли', textStyle: { fontSize: 14 } },
                tooltip: {
                    trigger: 'item',
                    formatter: '{b}: {c}% ({d}%)'
                },
                legend: {
                    orient: 'vertical',
                    right: 10,
                    top: 40,
                    bottom: 20
                },
                series: [{
                    type: 'pie',
                    radius: ['40%', '70%'],
                    center: ['40%', '55%'],
                    avoidLabelOverlap: true,
                    label: { show: true, formatter: '{b}\n{c}%' },
                    emphasis: {
                        label: { show: true, fontSize: 14, fontWeight: 'bold' }
                    },
                    data: marketShares.map(r => ({
                        name: r.name,
                        value: r.share,
                        itemStyle: r.name === monopolyName
                            ? { borderColor: '#1f3a8a', borderWidth: 2 }
                            : {}
                    }))
                }]
            });
            window.addEventListener('resize', () => shareChart.resize());
        }
    }

    window.addEventListener('resize', () => {
        revenueChart.resize();
        ratiosChart.resize();
        indexChart.resize();
        radarChart.resize();
    });
});