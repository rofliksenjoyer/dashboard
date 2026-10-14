document.addEventListener('DOMContentLoaded', () => {
    if (typeof MONOPOLY_ID === 'undefined') return;

    fetch(`/api/monopolies/${MONOPOLY_ID}`)
        .then(r => r.json())
        .then(res => {
            const m = res.data;
            if (!m) {
                document.getElementById('monopoly-name').textContent = 'Монополия не найдена';
                return;
            }
            renderHeader(m);
            renderTopMetrics(m);
            renderCharts(m);
            renderBasicMetrics(m);
            renderCourtCases(m.court_cases);
        })
        .catch(err => console.error('Ошибка загрузки монополии:', err));

    // Модальное окно
    const modal = document.getElementById('chart-modal');
    if (modal) {
        modal.addEventListener('click', e => {
            if (e.target === modal) closeChartModal();
        });
        const closeBtn = modal.querySelector('.chart-modal-close');
        if (closeBtn) closeBtn.addEventListener('click', closeChartModal);
        document.addEventListener('keydown', e => {
            if (e.key === 'Escape') closeChartModal();
        });
    }
});


function renderHeader(m) {
    document.getElementById('monopoly-name').textContent = m.name;

    if (m.website) {
        const link = document.getElementById('monopoly-website');
        link.href = m.website;
        link.textContent = m.website;
        link.style.display = 'inline';
    }

    if (m.description) {
        const desc = document.getElementById('monopoly-description');
        desc.textContent = m.description;
        desc.style.display = 'block';
    }
}


function renderTopMetrics(m) {
    const periods = m.periods || [];
    const latest = periods[periods.length - 1];
    const container = document.getElementById('top-metrics');

    if (!latest || !latest.ratios) {
        container.innerHTML = '';
        return;
    }

    let html = '<div class="metric-panel">';
    if (m.country) {
        html += `
            <div class="metric-item">
                <span class="metric-label">Страна</span>
                <span class="metric-value">${m.country.name}</span>
            </div>`;
    }
    if (latest.ratios.hhi != null) {
        html += `
            <div class="metric-item">
                <span class="metric-label">HHI по отрасли (${latest.year})</span>
                <span class="metric-value">${latest.ratios.hhi}</span>
            </div>`;
    }
    if (latest.ratios.market_share != null) {
        html += `
            <div class="metric-item">
                <span class="metric-label">Доля рынка (${latest.year})</span>
                <span class="metric-value">${latest.ratios.market_share}%</span>
            </div>`;
    }
    html += '</div>';
    container.innerHTML = html;
}


const chartRegistry = {};

function safeChart(elId, builder) {
    const el = document.getElementById(elId);
    if (!el) {
        console.warn(`Контейнер #${elId} не найден — пропускаю`);
        return;
    }
    try {
        const chart = echarts.init(el);
        builder(chart);
        window.addEventListener('resize', () => chart.resize());
        chartRegistry[elId] = chart.getOption();
        el.addEventListener('click', () => openChartModal(elId));
    } catch (e) {
        console.error(`Ошибка инициализации графика #${elId}:`, e);
    }
}


let modalChart = null;

function openChartModal(elId) {
    const modal = document.getElementById('chart-modal');
    const body = document.getElementById('chart-modal-body');
    if (!modal || !body) return;

    body.innerHTML = '';
    modal.classList.add('open');

    modalChart = echarts.init(body);
    const options = chartRegistry[elId];
    if (options) {
        const enlarged = JSON.parse(JSON.stringify(options));
        if (enlarged.title?.[0]) enlarged.title[0].textStyle = { fontSize: 18 };
        if (enlarged.legend?.[0]) enlarged.legend[0].textStyle = { fontSize: 14 };
        modalChart.setOption(enlarged);
    }
    setTimeout(() => modalChart.resize(), 50);
}


function closeChartModal() {
    const modal = document.getElementById('chart-modal');
    if (!modal) return;
    modal.classList.remove('open');
    if (modalChart) {
        modalChart.dispose();
        modalChart = null;
    }
}


function renderCharts(m) {
    const periods = m.periods || [];
    const labels = periods.map(p => String(p.year));

    const revenues = periods.map(p => p.values?.revenue?.value ?? null);
    const profits = periods.map(p => p.values?.net_profit?.value ?? null);
    const profitability = periods.map(p => p.ratios?.profitability ?? null);
    const roe = periods.map(p => p.ratios?.roe ?? null);
    const lerner = periods.map(p => p.ratios?.lerner ?? null);
    const hhi = periods.map(p => p.hhi ?? null);
    const autonomy = periods.map(p => p.ratios?.autonomy ?? null);
    const debtLoad = periods.map(p => p.ratios?.debt_load ?? null);

    // 1. Выручка и прибыль
    safeChart('chart-revenue', chart => {
        chart.setOption({
            title: { text: 'Динамика выручки и прибыли', textStyle: { fontSize: 14 } },
            tooltip: { trigger: 'axis' },
            legend: { data: ['Выручка', 'Чистая прибыль'], bottom: 0 },
            grid: { left: 60, right: 20, top: 40, bottom: 50 },
            xAxis: { type: 'category', data: labels },
            yAxis: { type: 'value' },
            series: [
                { name: 'Выручка', type: 'line', smooth: true, data: revenues, itemStyle: { color: '#1f3a8a' } },
                { name: 'Чистая прибыль', type: 'line', smooth: true, data: profits, itemStyle: { color: '#dc2626' } }
            ]
        });
    });

    // 2. Рентабельность
    safeChart('chart-ratios', chart => {
        chart.setOption({
            title: { text: 'Показатели рентабельности', textStyle: { fontSize: 14 } },
            tooltip: { trigger: 'axis', valueFormatter: v => v != null ? v + '%' : '—' },
            legend: { data: ['Рентабельность продаж', 'ROE'], bottom: 0 },
            grid: { left: 60, right: 20, top: 40, bottom: 50 },
            xAxis: { type: 'category', data: labels },
            yAxis: { type: 'value', axisLabel: { formatter: '{value}%' } },
            series: [
                { name: 'Рентабельность продаж', type: 'bar', data: profitability, itemStyle: { color: '#059669' } },
                { name: 'ROE', type: 'bar', data: roe, itemStyle: { color: '#7c3aed' } }
            ]
        });
    });

    // 3. Индекс Лернера
    safeChart('chart-lerner', chart => {
        chart.setOption({
            title: { text: 'Индекс Лернера (монопольная власть)', textStyle: { fontSize: 14 } },
            tooltip: { trigger: 'axis', valueFormatter: v => v != null ? v : '—' },
            grid: { left: 60, right: 20, top: 40, bottom: 30 },
            xAxis: { type: 'category', data: labels },
            yAxis: { type: 'value' },
            series: [
                { name: 'Индекс Лернера', type: 'bar', data: lerner, itemStyle: { color: '#b45309' }, barWidth: '50%' }
            ]
        });
    });

    // 4. HHI
    safeChart('chart-hhi', chart => {
        chart.setOption({
            title: { text: 'HHI по отрасли', textStyle: { fontSize: 14 } },
            tooltip: { trigger: 'axis', valueFormatter: v => v != null ? v : '—' },
            grid: { left: 60, right: 20, top: 40, bottom: 30 },
            xAxis: { type: 'category', data: labels },
            yAxis: { type: 'value', min: 0, max: 10000 },
            series: [
                { name: 'HHI', type: 'bar', data: hhi, itemStyle: { color: '#1f3a8a' }, barWidth: '50%' }
            ]
        });
    });

    // 5. Автономия
    safeChart('chart-autonomy', chart => {
        chart.setOption({
            title: { text: 'Коэффициент автономии', textStyle: { fontSize: 14 } },
            tooltip: { trigger: 'axis' },
            grid: { left: 60, right: 20, top: 40, bottom: 30 },
            xAxis: { type: 'category', data: labels },
            yAxis: { type: 'value', min: 0, max: 1 },
            series: [
                { name: 'Автономия', type: 'line', smooth: true, data: autonomy, itemStyle: { color: '#0e7490' } }
            ]
        });
    });

    // 6. Долговая нагрузка
    safeChart('chart-debt-load', chart => {
        chart.setOption({
            title: { text: 'Коэффициент долговой нагрузки', textStyle: { fontSize: 14 } },
            tooltip: { trigger: 'axis' },
            grid: { left: 60, right: 20, top: 40, bottom: 30 },
            xAxis: { type: 'category', data: labels },
            yAxis: { type: 'value' },
            series: [
                { name: 'Долговая нагрузка', type: 'line', smooth: true, data: debtLoad, itemStyle: { color: '#be123c' } }
            ]
        });
    });

    // 7. Темпы прироста
    const growth = m.growth_rates || [];
    const growthLabels = growth.map(g => String(g.year));
    const revenueGrowth = growth.map(g => g.revenue_growth);
    const profitGrowth = growth.map(g => g.profit_growth);

    safeChart('chart-growth', chart => {
        chart.setOption({
            title: { text: 'Темпы прироста, % к предыдущему году', textStyle: { fontSize: 14 } },
            tooltip: { trigger: 'axis', valueFormatter: v => v != null ? v + '%' : '—' },
            legend: { data: ['Прирост выручки', 'Прирост прибыли'], bottom: 0 },
            grid: { left: 60, right: 20, top: 40, bottom: 50 },
            xAxis: { type: 'category', data: growthLabels },
            yAxis: { type: 'value', axisLabel: { formatter: '{value}%' } },
            series: [
                { name: 'Прирост выручки', type: 'bar', data: revenueGrowth, itemStyle: { color: '#059669' } },
                { name: 'Прирост прибыли', type: 'bar', data: profitGrowth, itemStyle: { color: '#dc2626' } }
            ]
        });
    });

    // 8. Radar
    safeChart('chart-radar', chart => {
        const norm = (value, max) => {
            if (value == null) return 0;
            const v = Math.max(0, value);
            return Math.round(Math.min(v / max, 1) * 100);
        };

        const seriesData = periods.map(p => {
            const r = p.ratios || {};
            return {
                name: String(p.year),
                value: [
                    norm(r.profitability, 50),
                    norm(r.roe, 50),
                    norm(r.autonomy, 1),
                    norm(r.debt_load, 5),
                    norm(r.lerner, 1)
                ],
                raw: [r.profitability, r.roe, r.autonomy, r.debt_load, r.lerner]
            };
        });

        chart.setOption({
            title: { text: 'Комплексная оценка (нормализовано, %)', textStyle: { fontSize: 14 } },
            tooltip: {
                trigger: 'item',
                formatter: params => {
                    const raw = params.data.raw || [];
                    const names = [
                        'Рентабельность продаж', 'ROE', 'Автономия',
                        'Долговая нагрузка', 'Лернер'
                    ];
                    let html = `<b>${params.name}</b><br/>`;
                    names.forEach((n, i) => {
                        html += `${n}: ${raw[i] != null ? raw[i] : '—'}<br/>`;
                    });
                    return html;
                }
            },
            legend: { data: periods.map(p => String(p.year)), bottom: 0 },
            radar: {
                indicator: [
                    { name: 'Рентабельность продаж', max: 100 },
                    { name: 'ROE', max: 100 },
                    { name: 'Автономия', max: 100 },
                    { name: 'Долговая нагрузка', max: 100 },
                    { name: 'Лернер', max: 100 }
                ],
                radius: '60%'
            },
            series: [{
                type: 'radar',
                data: seriesData.map(d => ({
                    name: d.name,
                    value: d.value,
                    raw: d.raw,
                    areaStyle: { opacity: 0.15 }
                }))
            }]
        });
    });

    // 9. Доля рынка
    const latest = periods[periods.length - 1];
    if (latest && m.industry?.id && m.country?.id) {
        fetch(`/api/industries/${m.industry.id}/market-shares?year=${latest.year}&country=${m.country.id}`)
            .then(r => r.json())
            .then(res => renderMarketShares(res.data || [], m.name, latest.year));
    }
}


function renderMarketShares(shares, monopolyName, year) {
    if (!shares.length) return;
    safeChart('chart-market-share', chart => {
        chart.setOption({
            title: { text: `Доля рынка по отрасли (${year})`, textStyle: { fontSize: 14 } },
            tooltip: { trigger: 'item', formatter: '{b}: {c}% ({d}%)' },
            legend: { orient: 'vertical', right: 10, top: 40, bottom: 20 },
            series: [{
                type: 'pie',
                radius: ['40%', '70%'],
                center: ['40%', '55%'],
                label: { show: true, formatter: '{b}\n{c}%' },
                emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
                data: shares.map(s => ({
                    name: s.name,
                    value: s.share,
                    itemStyle: s.name === monopolyName
                        ? { borderColor: '#1f3a8a', borderWidth: 2 }
                        : {}
                }))
            }]
        });
    });
}


function renderBasicMetrics(m) {
    const periods = m.periods || [];
    const container = document.getElementById('basic-metrics');

    if (!periods.length) {
        container.innerHTML = '';
        return;
    }

    let rows = '';
    periods.forEach(p => {
        const values = p.values || {};
        rows += `
            <tr>
                <td>${p.year}</td>
                <td>${fmt(values.revenue?.value)}</td>
                <td>${fmt(values.equity?.value)}</td>
                <td>${fmt(values.assets?.value)}</td>
                <td>${fmt(values.net_profit?.value)}</td>
                <td>${fmt(values.credits?.value)}</td>
            </tr>`;
    });

    container.innerHTML = `
        <h2>Базовые показатели по годам (млн руб.)</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Год</th>
                    <th>Выручка от продаж</th>
                    <th>Собственный капитал</th>
                    <th>Активы</th>
                    <th>Чистая прибыль</th>
                    <th>Кредиты и займы</th>
                </tr>
            </thead>
            <tbody>${rows}</tbody>
        </table>`;
}


function renderCourtCases(cases) {
    const container = document.getElementById('court-cases-container');
    if (!cases || !cases.length) {
        container.innerHTML = '<p class="muted">Судебные дела не найдены.</p>';
        return;
    }
    let html = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Номер дела</th>
                    <th>Суд</th>
                    <th>Дата</th>
                    <th>Статус</th>
                    <th>Ссылка</th>
                </tr>
            </thead>
            <tbody>`;
    cases.forEach(c => {
        html += `
            <tr>
                <td>${c.case_number}</td>
                <td>${c.court_name}</td>
                <td>${c.decision_date || '—'}</td>
                <td><span class="status status-${c.status}">${c.status}</span></td>
                <td>${c.decision_link ? `<a href="${c.decision_link}" target="_blank">Решение</a>` : '—'}</td>
            </tr>`;
    });
    html += '</tbody></table>';
    container.innerHTML = html;
}


function fmt(v, suffix = '') {
    if (v == null) return '—';
    return v + suffix;
}