document.addEventListener('DOMContentLoaded', () => {
    const infoEl = document.getElementById('sector-info');
    const gridEl = document.getElementById('company-grid');
    const yearSelect = document.getElementById('year-select');
    let currentYear = null;

    function badgeInfo(t) {
        const map = {
            natural:  { label: 'Естественная монополия',        bg: '#fef3c7', color: '#92400e', border: '#fcd34d' },
            resource: { label: 'Ресурсная монополия',            bg: '#dcfce7', color: '#166534', border: '#86efac' },
            platform: { label: 'Платформенная монополия',        bg: '#ede9fe', color: '#5b21b6', border: '#c4b5fd' },
            hightech: { label: 'Высокотехнологичная монополия',  bg: '#dbeafe', color: '#1e40af', border: '#93c5fd' },
        };
        return map[t] || { label: t || '—', bg: '#f1f5f9', color: '#475569', border: '#cbd5e1' };
    }

    function loadYears() {
        return fetch('/api/years').then(r => r.json()).then(res => {
            const years = res.data || [];
            yearSelect.innerHTML = '';
            years.forEach(y => {
                const opt = document.createElement('option');
                opt.value = y; opt.textContent = y;
                yearSelect.appendChild(opt);
            });
            if (years.length) {
                currentYear = years[years.length - 1];
                yearSelect.value = currentYear;
            }
        });
    }

    function load() {
        infoEl.innerHTML = '';
        gridEl.innerHTML = '<p class="muted">Загрузка…</p>';
        const params = new URLSearchParams();
        if (currentYear) params.set('year', currentYear);

        fetch(`/api/scopes/${SCOPE}/industries/${INDUSTRY_ID}?${params.toString()}`)
            .then(r => r.json())
            .then(res => {
                const d = res.data;
                if (!d) { gridEl.innerHTML = '<p class="muted">Нет данных.</p>'; return; }
                renderInfo(d);
                renderHhiChart(d);
                renderGrid(d);
            });
    }

    function renderInfo(d) {
        infoEl.innerHTML = `
            <div class="info-item">
                <div>
                    <div class="info-title">${escapeHtml(d.industry.name)}</div>
                    <div class="muted">${d.companies.length} компаний · ${d.year}</div>
                </div>
            </div>
            <div class="info-item info-center">
                <div class="info-big">${d.hhi != null ? d.hhi : '—'}</div>
                <div class="muted">HHI (индекс концентрации)</div>
            </div>
            <div class="info-item">
                <div class="muted">Выручка отрасли</div>
                <div class="info-mid">${fmtMoney(d.total_revenue)}</div>
            </div>
        `;
    }

    const chartRegistry = {};
    let modalChart = null;

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

    function renderHhiChart(d) {
    const dyn = d.hhi_dynamics || [];
    const labels = dyn.map(x => String(x.year));
    const values = dyn.map(x => x.hhi);

    safeChart('chart-hhi-dynamics', chart => {
        chart.setOption({
            title: { text: 'HHI по отрасли по годам', textStyle: { fontSize: 14 } },
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' },
                valueFormatter: v => v != null ? v : '—'
            },
            grid: { left: 60, right: 20, top: 40, bottom: 40 },
            xAxis: {
                type: 'category',
                data: labels,
                axisTick: { alignWithLabel: true }
            },
            yAxis: {
                type: 'value',
                min: 0,
                max: 10000,
                name: 'HHI',
                nameTextStyle: { color: '#64748b', fontSize: 11 }
            },
            series: [{
                name: 'HHI',
                type: 'bar',
                data: values.map(v => ({
                    value: v,
                    itemStyle: {
                        color: v == null ? '#cbd5e1'
                             : v > 2500 ? '#dc2626'
                             : v > 1500 ? '#f97316'
                             : '#22c55e',
                        borderRadius: [4, 4, 0, 0]
                    }
                })),
                barMaxWidth: 48,
                label: {
                    show: true,
                    position: 'top',
                    color: '#475569',
                    fontSize: 11,
                    formatter: p => p.value != null ? p.value : '—'
                },
                markLine: {
                    silent: true,
                    symbol: 'none',
                    lineStyle: { type: 'dashed', color: '#94a3b8' },
                    label: { formatter: '{b}', color: '#64748b', fontSize: 10, position: 'insideEndTop' },
                    data: [
                        { yAxis: 1500, name: '1500 — умеренная' },
                        { yAxis: 2500, name: '2500 — высокая' },
                        { yAxis: 10000, name: '10000 — полная монополия одной фирмы' }
                    ]
                }
            }]
        });
    });
}

    function renderGrid(d) {
        if (!d.companies.length) {
            gridEl.innerHTML = '<p class="muted">Компаний не найдено.</p>';
            return;
        }
        gridEl.innerHTML = '';
        d.companies.forEach((c, i) => {
            const badge = badgeInfo(c.badge_type);
            const card = document.createElement('a');
            card.className = 'company-card fade-in';
            card.href = `/company/${c.monopoly_id}`;
            card.style.animationDelay = (i * 0.06) + 's';
            card.innerHTML = `
                <div class="co-logo" style="background:${shade(c.color)}; color:${c.color}">
                    ${initials(c.short_name || c.name)}
                </div>
                <div class="co-name">${escapeHtml(c.name)}</div>
                <div class="badge" style="background:${badge.bg}; color:${badge.color}; border:1.5px solid ${badge.border}">
                    ${badge.label}
                </div>
                <div class="co-metrics">
                    <div><span class="muted">Доля</span><b>${c.share}%</b></div>
                    <div><span class="muted">Выручка</span><b>${fmtMoney(c.revenue)}</b></div>
                </div>
                <div class="co-open">Открыть досье &rarr;</div>
            `;
            gridEl.appendChild(card);
        });
    }

    function initials(name) {
        if (!name) return '?';
        const parts = name.trim().split(/\s+/).slice(0, 2);
        return parts.map(p => p[0]).join('').toUpperCase();
    }

    function shade(hex) {
        if (!hex) return '#f1f5f9';
        return hex + '18';
    }

    function fmtMoney(v) {
        if (v == null) return '—';
        return v.toLocaleString('ru-RU') + ' млн';
    }
    function escapeHtml(s) {
        return String(s).replace(/[&<>"']/g, c => ({
            '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
        }[c]));
    }

    yearSelect.addEventListener('change', () => {
        currentYear = yearSelect.value ? Number(yearSelect.value) : null;
        load();
    });

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

    loadYears().then(load);
});