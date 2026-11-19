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
            renderBreadcrumbs(m);
            renderHeader(m);
            renderTopMetrics(m);
            renderCharts(m);
            renderBasicMetrics(m);
            renderCourtCases(m.court_cases);
        })
        .catch(err => console.error('Ошибка загрузки монополии:', err));

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


function renderBreadcrumbs(m) {
    const el = document.getElementById('breadcrumbs');
    if (!el) return;
    const scope = m.country.market_scope;
    const scopeLabel = scope === 'ru' ? 'Национальные рынки'
                     : scope === 'world' ? 'Глобальные рынки'
                     : 'Весь мир';
    el.innerHTML = `
        <a href="/">Главное меню</a>
        <span class="sep">/</span>
        <a href="/scope/${scope}">${scopeLabel}</a>
        <span class="sep">/</span>
        <a href="/scope/${scope}/industry/${m.industry.id}">${m.industry.name}</a>
        <span class="sep">/</span>
        <span>${m.short_name || m.name}</span>
    `;
}


function renderHeader(m) {
    const nameEl = document.getElementById('monopoly-name');
    nameEl.textContent = m.name;

    const headerBlock = nameEl.parentElement;
    let logoImg = document.getElementById('monopoly-logo');
    if (!logoImg) {
        logoImg = document.createElement('img');
        logoImg.id = 'monopoly-logo';
        logoImg.className = 'monopoly-logo';
        headerBlock.insertBefore(logoImg, nameEl);
    }
    const logoUrl = m.logo_filename
        ? `/static/uploads/logos/${m.logo_filename}`
        : m.logo_url;
    if (logoUrl) {
        logoImg.src = logoUrl;
        logoImg.alt = m.name;
        logoImg.style.display = 'inline-block';
    } else {
        logoImg.style.display = 'none';
    }

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
    if (m.industry) {
        html += `
            <div class="metric-item">
                <span class="metric-label">Отрасль</span>
                <span class="metric-value">${m.industry.name}</span>
            </div>`;
    }
    if (m.employees) {
        html += `
            <div class="metric-item">
                <span class="metric-label">Сотрудников</span>
                <span class="metric-value">${m.employees} тыс.</span>
            </div>`;
    }
    html += '</div>';
    container.innerHTML = html;
}


const chartRegistry = {};

const marketState = {
    markets: [],
    companyName: '',
    companyId: null,
    selectedId: null,
    chart: null,
    requestToken: 0,
};

function safeChart(elId, builder) {
    const el = document.getElementById(elId);
    if (!el) return;
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
        const enlarged = {
    ...options,

    title: options.title?.map(t => ({
        ...t,
        textStyle: {
            ...t.textStyle,
            fontSize: 18
        }
    })),

    legend: options.legend?.map(l => ({
        ...l,
        textStyle: {
            ...l.textStyle,
            fontSize: 14
        }
    }))
};

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
    const autonomy = periods.map(p => p.ratios?.autonomy ?? null);
    const liabilities = periods.map(p => p.values?.liabilities?.value ?? null);
    const leverage = periods.map(p => p.ratios?.leverage ?? null);
    const curLabel = m.currency ? ' ' + currencyLabel(m.currency) : '';

    safeChart('chart-revenue', chart => {
        chart.setOption({
            title: { text: 'Динамика выручки и прибыли' + (m.currency ? ', млн ' + currencyLabel(m.currency) : ''), textStyle: { fontSize: 14 } },
            tooltip: { trigger: 'axis' },
            legend: { data: ['Выручка', 'Чистая прибыль'], bottom: 0 },
            grid: { left: 10, right: 20, top: 44, bottom: 50, containLabel: true },
            xAxis: { type: 'category', data: labels },
            yAxis: { type: 'value' },
            series: [
                { name: 'Выручка', type: 'line', smooth: true, data: revenues, itemStyle: { color: '#1f3a8a' } },
                { name: 'Чистая прибыль', type: 'line', smooth: true, data: profits, itemStyle: { color: '#dc2626' } }
            ]
        });
    });

    safeChart('chart-ratios', chart => {
        chart.setOption({
            title: { text: 'Показатели рентабельности', textStyle: { fontSize: 14 } },
            tooltip: { trigger: 'axis', valueFormatter: v => v != null ? v + '%' : '—' },
            legend: { data: ['Рентабельность продаж', 'ROE'], bottom: 0 },
            grid: { left: 10, right: 20, top: 44, bottom: 50, containLabel: true },
            xAxis: { type: 'category', data: labels },
            yAxis: { type: 'value', axisLabel: { formatter: '{value}%' } },
            series: [
                { name: 'Рентабельность продаж', type: 'bar', data: profitability, itemStyle: { color: '#059669' } },
                { name: 'ROE', type: 'bar', data: roe, itemStyle: { color: '#7c3aed' } }
            ]
        });
    });

    const autonomyValues = autonomy.filter(v => v != null && isFinite(v));
    const autonomyMin = Math.floor(Math.min(0, ...(autonomyValues.length ? autonomyValues : [0])) * 10) / 10;
    const autonomyMax = Math.max(1, Math.ceil(Math.max(1, ...(autonomyValues.length ? autonomyValues : [1])) * 10) / 10);

    safeChart('chart-autonomy', chart => {
        chart.setOption({
            title: { text: 'Коэффициент автономии', textStyle: { fontSize: 14 } },
            tooltip: { trigger: 'axis' },
            grid: { left: 10, right: 20, top: 44, bottom: 30, containLabel: true },
            xAxis: { type: 'category', data: labels },
            yAxis: {
                type: 'value',
                min: autonomyMin,
                max: autonomyMax,
                axisLabel: { formatter: v => v.toFixed(2) }
            },
            series: [
                { name: 'Автономия', type: 'line', smooth: true, data: autonomy, itemStyle: { color: '#0e7490' } }
            ]
        });
    });

    safeChart('chart-debt-load', chart => {
        chart.setOption({
            title: { text: 'Обязательства, млн' + curLabel, textStyle: { fontSize: 14 } },
            tooltip: { trigger: 'axis' },
            legend: { data: ['Обязательства, млн' + curLabel, 'Финансовый рычаг (обязательства / капитал)'], bottom: 0 },
            grid: { left: 10, right: 10, top: 44, bottom: 50, containLabel: true },
            xAxis: { type: 'category', data: labels },
            yAxis: [
                { type: 'value' },
                { type: 'value', name: 'рычаг, ×', splitLine: { show: false } }
            ],
            series: [
                { name: 'Обязательства, млн' + curLabel, type: 'bar', data: liabilities, itemStyle: { color: '#be123c' } },
                { name: 'Финансовый рычаг (обязательства / капитал)', type: 'line', yAxisIndex: 1, smooth: true, data: leverage, itemStyle: { color: '#1f3a8a' } }
            ]
        });
    });

    const growth = m.growth_rates || [];
    const growthLabels = growth.map(g => String(g.year));
    const revenueGrowth = growth.map(g => g.revenue_growth);
    const profitGrowth = growth.map(g => g.profit_growth);

    safeChart('chart-growth', chart => {
        chart.setOption({
            title: { text: 'Темпы прироста, % к предыдущему году', textStyle: { fontSize: 14 } },
            tooltip: { trigger: 'axis', valueFormatter: v => v != null ? v + '%' : '—' },
            legend: { data: ['Прирост выручки', 'Прирост прибыли'], bottom: 0 },
            grid: { left: 10, right: 20, top: 44, bottom: 50, containLabel: true },
            xAxis: { type: 'category', data: growthLabels },
            yAxis: { type: 'value', axisLabel: { formatter: '{value}%' } },
            series: [
                { name: 'Прирост выручки', type: 'bar', data: revenueGrowth, itemStyle: { color: '#059669' } },
                { name: 'Прирост прибыли', type: 'bar', data: profitGrowth, itemStyle: { color: '#dc2626' } }
            ]
        });
    });

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
                    norm(r.leverage, 5),
                ],
                raw: [r.profitability, r.roe, r.autonomy, r.leverage]
            };
        });

        chart.setOption({
            title: { text: 'Комплексная оценка', textStyle: { fontSize: 14 } },
            tooltip: {
                trigger: 'item',
                formatter: params => {
                    const raw = params.data.raw || [];
                    const names = [
                        'Рентабельность продаж', 'ROE', 'Автономия', 'Финансовый рычаг'
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
                    { name: 'Финансовый рычаг', max: 100 }
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

    renderMarketSection(m);
}


function renderMarketSection(m) {
    const markets = m.markets || [];
    const listEl = document.getElementById('markets-list');

    marketState.markets = markets;
    marketState.companyName = m.short_name || m.name;
    marketState.companyId = m.id;

    if (!listEl) return;

    if (!markets.length) {
        listEl.innerHTML = '';
        return;
    }

    listEl.innerHTML = `
        <h2>Рынки компании</h2>
        <div class="markets-chips">
            ${markets.map(mk => `
                <button type="button" class="market-chip ${mk.is_main ? 'market-chip-main' : ''}"
                        data-market-id="${mk.id}"
                        title="Показать долю на рынке «${escapeHtml(mk.name)}»">
                    ${escapeHtml(mk.name)}
                    <b>${mk.share}%</b>
                    ${mk.is_main ? '<em>главный</em>' : ''}
                </button>`).join('')}
        </div>`;

    listEl.querySelectorAll('.market-chip').forEach(btn => {
        btn.addEventListener('click', () => selectMarket(Number(btn.dataset.marketId)));
    });

    const requested = Number(new URLSearchParams(window.location.search).get('market'));
    const initial = markets.find(x => x.id === requested)
        || markets.find(x => x.is_main)
        || markets[0];
    selectMarket(initial.id);
}


function selectMarket(marketId) {
    const market = marketState.markets.find(x => x.id === marketId);
    if (!market) return;

    marketState.selectedId = marketId;

    document.querySelectorAll('#markets-list .market-chip').forEach(btn => {
        const active = Number(btn.dataset.marketId) === marketId;
        btn.classList.toggle('market-chip-active', active);
        btn.setAttribute('aria-pressed', active ? 'true' : 'false');
    });

    const url = new URL(window.location.href);
    url.searchParams.set('market', marketId);
    history.replaceState(null, '', url);

    const token = ++marketState.requestToken;
    fetch(`/api/markets/${marketId}`)
        .then(r => r.json())
        .then(res => {
            if (token !== marketState.requestToken) return;
            renderMarketSharePie(res.data, marketState.companyName, marketState.companyId);
        })
        .catch(err => {
            if (token !== marketState.requestToken) return;
            console.error('Ошибка загрузки рынка:', err);
            renderMarketChartMessage('Не удалось загрузить данные рынка');
        });
}


function initMarketChart(el) {
    marketState.chart = echarts.init(el);
    window.addEventListener('resize', () => marketState.chart.resize());
    el.addEventListener('click', () => openChartModal('chart-market-share'));
    return marketState.chart;
}


function renderMarketChartMessage(text) {
    const el = document.getElementById('chart-market-share');
    if (!el) return;
    if (!marketState.chart) initMarketChart(el);
    marketState.chart.setOption({
        title: { text, textStyle: { fontSize: 14 } },
        series: []
    }, true);
    chartRegistry['chart-market-share'] = marketState.chart.getOption();
}


function renderMarketSharePie(data, companyName, companyId) {
    const el = document.getElementById('chart-market-share');
    if (!el) return;

    if (!data || !data.companies || !data.companies.length) {
        renderMarketChartMessage('Нет данных по выбранному рынку');
        return;
    }

    if (!marketState.chart) initMarketChart(el);

    const isCurrent = c => (companyId != null && c.monopoly_id === companyId)
        || c.short_name === companyName
        || c.name === companyName;

    const series = data.companies.map(c => ({
        name: c.short_name || c.name,
        value: c.share,
        itemStyle: isCurrent(c)
            ? { borderColor: '#1f3a8a', borderWidth: 3 }
            : {}
    }));

    if (data.others > 0) {
        series.push({
            name: 'Остальные компании',
            value: data.others,
            itemStyle: { color: '#cbd5e1' }
        });
    }

    const marketName = data.name || '';

    marketState.chart.setOption({
        title: { text: `Доля рынка — ${marketName}`, textStyle: { fontSize: 14 } },
        tooltip: { trigger: 'item', formatter: '{b}: {c}% ({d}%)' },
        legend: { orient: 'vertical', right: 10, top: 40, bottom: 20 },
        series: [{
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['40%', '55%'],
            label: { show: true, formatter: '{b}\n{c}%' },
            emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
            data: series
        }]
    }, true);
    chartRegistry['chart-market-share'] = marketState.chart.getOption();
}


function renderBasicMetrics(m) {
    const periods = m.periods || [];
    const columns = m.table_columns || [];
    const container = document.getElementById('basic-metrics');

    if (!periods.length || !columns.length) {
        container.innerHTML = '';
        return;
    }

    let head = '<tr><th>Год</th>';
    columns.forEach(c => { head += `<th>${escapeHtml(c.label)}</th>`; });
    head += '</tr>';

    let rows = '';
    periods.forEach(p => {
        const t = p.table || {};
        rows += `<tr><td>${p.year}</td>`;
        columns.forEach(c => {
            const star = (c.code === 'liabilities' && p.liabilities_basis === 'credits' && t[c.code] != null) ? '*' : '';
            rows += `<td>${fmt(t[c.code])}${star}</td>`;
        });
        rows += '</tr>';
    });

    container.innerHTML = `
        <h2>Базовые показатели по годам (млн${m.currency ? ' ' + currencyLabel(m.currency) : ''})</h2>
        <div class="table-scroll">
            <table class="data-table">
                <thead>${head}</thead>
                <tbody>${rows}</tbody>
            </table>
        </div>
        ${periods.some(p => p.liabilities_basis === 'credits') ? '<p class="muted" style="font-size:12px">* нет данных по активам или капиталу — показаны только кредиты и займы из отчётности.</p>' : ''}`;
}


const STATUS_LABEL = {
    won: 'Выиграно',
    lost: 'Проиграно',
    pending: 'Рассматривается',
};


function renderCourtCases(cases) {
    const container = document.getElementById('court-cases-container');
    if (!cases || !cases.length) {
        container.innerHTML = '<p class="muted">—</p>';
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
                <td><span class="status status-${c.status}">${STATUS_LABEL[c.status] || c.status}</span></td>
                <td>${c.decision_link ? `<a href="${c.decision_link}" target="_blank">Решение</a>` : '—'}</td>
            </tr>`;
    });
    html += '</tbody></table>';
    container.innerHTML = html;
}


const CURRENCY_LABEL = {
    RUB: 'руб.', USD: 'долл.', EUR: 'евро', CNY: 'юан.', NOK: 'крон NOK', SEK: 'крон SEK',
    JPY: 'иен', KRW: 'вон', TWD: 'NT$', CHF: 'CHF', GBP: 'фунт.', SAR: 'SAR', CAD: 'CAD'
};
function currencyLabel(code) { return code ? (CURRENCY_LABEL[code] || code) : ''; }

function fmt(v) {
    if (v == null) return '—';
    return v.toLocaleString('ru-RU');
}

function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({
        '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
    }[c]));
}
