document.addEventListener('DOMContentLoaded', () => {
    const infoEl = document.getElementById('sector-info');
    const flagsEl = document.getElementById('sector-flags');
    const gridEl = document.getElementById('company-grid');
    const yearSelect = document.getElementById('year-select');
    const typeSelect = document.getElementById('type-select');
    
    let currentYear = null;
    let currentType = null;
    let countryNotes = [];
    let currentIndustry = null;

    const FLAG_SVG = {
        RU: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 9 6'><rect width='9' height='2' fill='%23ffffff'/><rect y='2' width='9' height='2' fill='%230039A6'/><rect y='4' width='9' height='2' fill='%23D52B1E'/></svg>",
        US: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 9 6'><rect width='9' height='6' fill='%23ffffff'/><g fill='%23B22234'><rect width='9' height='0.46'/><rect y='0.92' width='9' height='0.46'/><rect y='1.84' width='9' height='0.46'/><rect y='2.76' width='9' height='0.46'/><rect y='3.68' width='9' height='0.46'/><rect y='4.6' width='9' height='0.46'/><rect y='5.52' width='9' height='0.46'/></g><rect width='4' height='3.23' fill='%233C3B6E'/></svg>",
        CN: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 9 6'><rect width='9' height='6' fill='%23DE2910'/><polygon points='1.5,1 1.8,1.9 2.7,1.9 2,2.5 2.3,3.4 1.5,2.8 0.7,3.4 1,2.5 0.3,1.9 1.2,1.9' fill='%23FFDE00'/></svg>",
        DE: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 9 6'><rect width='9' height='2' fill='%23000000'/><rect y='2' width='9' height='2' fill='%23DD0000'/><rect y='4' width='9' height='2' fill='%23FFCE00'/></svg>",
        GB: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 30'><rect width='60' height='30' fill='%23012169'/><path d='M0,0 L60,30 M60,0 L0,30' stroke='%23fff' stroke-width='6'/><path d='M0,0 L60,30 M60,0 L0,30' stroke='%23C8102E' stroke-width='4'/><path d='M30,0 V30 M0,15 H60' stroke='%23fff' stroke-width='10'/><path d='M30,0 V30 M0,15 H60' stroke='%23C8102E' stroke-width='6'/></svg>",
        FR: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 9 6'><rect width='3' height='6' fill='%23002395'/><rect x='3' width='3' height='6' fill='%23ffffff'/><rect x='6' width='3' height='6' fill='%23ED2939'/></svg>",
        JP: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 9 6'><rect width='9' height='6' fill='%23ffffff'/><circle cx='4.5' cy='3' r='1.8' fill='%23BC002D'/></svg>",
        IN: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 9 6'><rect width='9' height='2' fill='%23FF9933'/><rect y='2' width='9' height='2' fill='%23ffffff'/><rect y='4' width='9' height='2' fill='%23138808'/><circle cx='4.5' cy='3' r='0.6' fill='none' stroke='%23000080' stroke-width='0.2'/></svg>",
        BR: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 9 6'><rect width='9' height='6' fill='%23009c3b'/><polygon points='4.5,0.5 8.5,3 4.5,5.5 0.5,3' fill='%23FEDF00'/><circle cx='4.5' cy='3' r='1' fill='%23002776'/></svg>",
        KR: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 9 6'><rect width='9' height='6' fill='%23ffffff'/><circle cx='4.5' cy='3' r='1.2' fill='%23CD2E3A'/><path d='M3.3,3 a1.2,1.2 0 0,0 2.4,0' fill='%230047A0'/></svg>",
        IT: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 9 6'><rect width='3' height='6' fill='%23009246'/><rect x='3' width='3' height='6' fill='%23ffffff'/><rect x='6' width='3' height='6' fill='%23CE2B37'/></svg>",
        CA: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 9 6'><rect width='9' height='6' fill='%23ffffff'/><rect width='2.25' height='6' fill='%23FF0000'/><rect x='6.75' width='2.25' height='6' fill='%23FF0000'/><polygon points='4.5,1 4.8,2 5.5,1.6 5.2,2.5 6,2.7 5,3.2 5.2,4 4.5,3.5 3.8,4 4,3.2 3,2.7 3.8,2.5 3.5,1.6 4.2,2' fill='%23FF0000'/></svg>",
        AU: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 9 6'><rect width='9' height='6' fill='%2300008B'/></svg>",
        NL: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 9 6'><rect width='9' height='2' fill='%23AE1C28'/><rect y='2' width='9' height='2' fill='%23ffffff'/><rect y='4' width='9' height='2' fill='%23214768'/></svg>",
        ES: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 9 6'><rect width='9' height='1.5' fill='%23AA151B'/><rect y='1.5' width='9' height='3' fill='%23F1BF00'/><rect y='4.5' width='9' height='1.5' fill='%23AA151B'/></svg>",
    };

    function flagSrc(country) {
        if (country && country.country_code) {
            const code = country.country_code.toUpperCase();
            if (FLAG_SVG[code]) return FLAG_SVG[code];
        }
        return "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 9 6'><rect width='9' height='6' fill='%23cbd5e1'/></svg>";
    }

    const modal = document.getElementById('note-modal');
    const modalBody = document.getElementById('note-modal-body');
    const modalClose = modal?.querySelector('.note-modal-close');

    function openNoteModal(countryId) {
        const country = countryNotes.find(x => x.country_id === countryId);
        if (!country || !modal || !modalBody) return;

        const src = flagSrc(country);
        const title = country.title || country.country_name;
        const body = country.body
            ? escapeHtml(country.body).replace(/\n/g, '<br>')
            : '<span class="muted">Информация ещё не добавлена.</span>';

        modalBody.innerHTML = `
            <div class="note-head">
                <img class="note-flag-img" src="${src}" alt="">
                <div>
                    <div class="note-title">${escapeHtml(title)}</div>
                    <div class="muted">${escapeHtml(country.country_name)} — ${escapeHtml(currentIndustry || '')}</div>
                </div>
            </div>

            <div class="note-stats">
                <div class="stat-box">
                    <div class="stat-label">HHI в стране</div>
                    <div class="stat-mid">${country.hhi != null ? country.hhi : '—'}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Доля лидера</div>
                    <div class="stat-mid">${country.top_share ? country.top_share.toFixed(1) + '%' : '—'}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Компаний</div>
                    <div class="stat-mid">${country.companies_count || 0}</div>
                </div>
            </div>

            ${country.top_companies && country.top_companies.length ? `
                <div class="note-top">
                    <div class="stat-label" style="margin-bottom:.5rem;">Лидеры отрасли</div>
                    <ol class="top-list">
                        ${country.top_companies.map(tc => `
                            <li>
                                <span class="top-name">${escapeHtml(tc.name)}</span>
                                <span class="top-share">${tc.share}%</span>
                            </li>`).join('')}
                    </ol>
                </div>` : ''}

            <div class="note-body">${body}</div>
        `;
        modal.classList.add('open');
    }

    function closeNoteModal() {
        if (modal) modal.classList.remove('open');
    }

    if (modal) {
        modal.addEventListener('click', e => {
            if (e.target === modal) closeNoteModal();
        });
        modalClose?.addEventListener('click', closeNoteModal);
        document.addEventListener('keydown', e => {
            if (e.key === 'Escape') closeNoteModal();
        });
    }

    function badgeInfo(t) {
        if (!t) {
            return { label: 'Без типа', bg: '#f1f5f9', color: '#475569', border: '#cbd5e1' };
        }
        const hue = stringToHue(t);
        return {
            label: t,
            bg: `hsl(${hue}, 85%, 94%)`,
            color: `hsl(${hue}, 65%, 30%)`,
            border: `hsl(${hue}, 70%, 75%)`,
        };
    }

    function stringToHue(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = str.charCodeAt(i) + ((hash << 5) - hash);
            hash = hash & hash;
        }
        return Math.abs(hash) % 360;
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
        flagsEl.innerHTML = '<p class="muted">Загрузка…</p>';
        gridEl.innerHTML = '<p class="muted">Загрузка…</p>';
        
        const params = new URLSearchParams();
        if (currentYear) params.set('year', currentYear);
        if (currentType) params.set('type', currentType);
        // Если мы в национальном контуре и передали country_id
        if (typeof COUNTRY_ID !== 'undefined' && COUNTRY_ID) {
            params.set('country', COUNTRY_ID);
        }

        fetch(`/api/scopes/${SCOPE}/industries/${INDUSTRY_ID}?${params.toString()}`)
            .then(r => r.json())
            .then(res => {
                const d = res.data;
                if (!d) { gridEl.innerHTML = '<p class="muted">Нет данных.</p>'; return; }
                countryNotes = d.country_notes || [];
                currentIndustry = d.industry?.name || '';
                
                // Заполняем селект типов монополий (только 1 раз)
                if (typeSelect && typeSelect.options.length === 1 && d.monopoly_types) {
                    d.monopoly_types.forEach(t => {
                        typeSelect.innerHTML += `<option value="${t.id}">${t.name}</option>`;
                    });
                }

                renderInfo(d);
                renderFlags(d);
                renderHhiChart(d);
                renderGrid(d);
            });
    }

    function renderInfo(d) {
        const year = d.year != null ? d.year : '';
        const count = d.companies.length;

        infoEl.innerHTML = `
            <div class="sector-cell">
                <div class="sector-value small">Компаний: ${count} · ${year}</div>
            </div>
            <div class="sector-cell">
                <div class="sector-value">${d.hhi != null ? d.hhi : '—'}</div>
                <div class="sector-label">HHI (индекс концентрации)</div>
            </div>
            <div class="sector-cell">
                <div class="sector-value">${fmtMoney(d.total_revenue)}</div>
                <div class="sector-label">Выручка отрасли</div>
            </div>
        `;
    }

    function renderFlags(d) {
        const notes = d.country_notes || [];
        if (!notes.length) {
            flagsEl.innerHTML = '<span class="muted">Нет данных по странам для этой отрасли.</span>';
            return;
        }
        flagsEl.innerHTML = `
            <div class="flags-label">Сравнение отрасли по странам</div>
            <div class="flags-row">
                ${notes.map(n => `
                    <button type="button" class="flag-chip" data-country-id="${n.country_id}"
                            title="${escapeHtml(n.country_name)}${n.body ? '' : ' — заметка не заполнена'}">
                        <img class="flag-img" src="${flagSrc(n)}" alt="">
                        <span class="flag-name">${escapeHtml(n.country_name)}</span>
                    </button>
                `).join('')}
            </div>
        `;
        flagsEl.querySelectorAll('.flag-chip').forEach(btn => {
            btn.addEventListener('click', () => openNoteModal(Number(btn.dataset.countryId)));
        });
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
        const cm = document.getElementById('chart-modal');
        const body = document.getElementById('chart-modal-body');
        if (!cm || !body) return;
        body.innerHTML = '';
        cm.classList.add('open');
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
        const cm = document.getElementById('chart-modal');
        if (!cm) return;
        cm.classList.remove('open');
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
                xAxis: { type: 'category', data: labels, axisTick: { alignWithLabel: true } },
                yAxis: {
                    type: 'value', min: 0, max: 10000,
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
                        show: true, position: 'top', color: '#475569',
                        fontSize: 11, formatter: p => p.value != null ? p.value : '—'
                    },
                    markLine: {
                        silent: true, symbol: 'none',
                        lineStyle: { type: 'dashed', color: '#94a3b8' },
                        label: {
                            formatter: '{b}', color: '#64748b',
                            fontSize: 10, position: 'insideEndTop'
                        },
                        data: [
                            { yAxis: 1500, name: '1500 — умеренная' },
                            { yAxis: 2500, name: '2500 — высокая' }
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
            const badge = badgeInfo(c.monopoly_type);
            const card = document.createElement('a');
            card.className = 'company-card fade-in';
            card.href = `/company/${c.monopoly_id}`;
            card.style.animationDelay = (i * 0.04) + 's';

            const logoSrc = c.logo_filename
                ? `/static/uploads/logos/${c.logo_filename}`
                : c.logo_url;

            const logoBlock = logoSrc
                ? `<img class="co-logo-img" src="${logoSrc}" alt="">`
                : `<div class="co-logo" style="background:${shade(c.color)}; color:${c.color || '#475569'}">${initials(c.short_name || c.name)}</div>`;

            card.innerHTML = `
                ${logoBlock}
                <div class="co-name">${escapeHtml(c.name)}</div>
                <div class="muted">${escapeHtml(c.country_name || '')}</div>
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

    if (typeSelect) {
        typeSelect.addEventListener('change', () => {
            currentType = typeSelect.value ? Number(typeSelect.value) : null;
            load();
        });
    }

    const cm = document.getElementById('chart-modal');
    if (cm) {
        cm.addEventListener('click', e => {
            if (e.target === cm) closeChartModal();
        });
        const closeBtn = cm.querySelector('.chart-modal-close');
        if (closeBtn) closeBtn.addEventListener('click', closeChartModal);
        document.addEventListener('keydown', e => {
            if (e.key === 'Escape') closeChartModal();
        });
    }

    loadYears().then(load);
});