document.addEventListener('DOMContentLoaded', () => {
    const infoEl = document.getElementById('sector-info');
    const flagsEl = document.getElementById('sector-flags');
    const yearSelect = document.getElementById('year-select');
    const typeSelect = document.getElementById('type-select');
    const marketSelect = document.getElementById('market-select');

    let currentYear = null;
    let currentType = null;
    let currentMarket = null;
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
        NO: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 22 16'><rect width='22' height='16' fill='%23BA0C2F'/><rect x='6' width='4' height='16' fill='%23ffffff'/><rect y='6' width='22' height='4' fill='%23ffffff'/><rect x='7' width='2' height='16' fill='%2300205B'/><rect y='7' width='22' height='2' fill='%2300205B'/></svg>",
        SE: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 10'><rect width='16' height='10' fill='%23006AA7'/><rect x='5' width='2' height='10' fill='%23FECC00'/><rect y='4' width='16' height='2' fill='%23FECC00'/></svg>",
        CH: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' fill='%23D52B1E'/><rect x='13' y='6' width='6' height='20' fill='%23ffffff'/><rect x='6' y='13' width='20' height='6' fill='%23ffffff'/></svg>",
        TW: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 20'><rect width='30' height='20' fill='%23FE0000'/><rect width='15' height='10' fill='%23000095'/><circle cx='7.5' cy='5' r='3' fill='%23ffffff'/><circle cx='7.5' cy='5' r='2.2' fill='%23000095'/><circle cx='7.5' cy='5' r='1.7' fill='%23ffffff'/></svg>",
        SA: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 20'><rect width='30' height='20' fill='%23006C35'/><rect x='6' y='6' width='18' height='1.6' rx='0.8' fill='%23ffffff'/><rect x='9' y='9' width='12' height='1.2' rx='0.6' fill='%23ffffff'/><rect x='7' y='14' width='16' height='1.1' fill='%23ffffff'/><rect x='6' y='13.6' width='2.2' height='1.9' fill='%23ffffff'/></svg>",
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

            ${country.markets && country.markets.length ? `
                <div class="note-top">
                    <div class="stat-label" style="margin-bottom:.5rem;">Статистика по рынкам страны</div>
                    <div class="market-stat-list">
                        ${country.markets.map(mk => `
                            <div class="market-stat-row">
                                <div class="msr-name">${escapeHtml(mk.market)}</div>
                                <div class="msr-meta">
                                    <span>Лидер: <b>${escapeHtml(mk.leader)}</b></span>
                                    <span>Доля лидера: <b>${mk.share}%</b></span>
                                    <span>HHI: <b>${mk.hhi != null ? mk.hhi : '—'}</b></span>
                                    <span>Монополизация: ${levelBadge(mk)}</span>
                                </div>
                            </div>`).join('')}
                    </div>
                </div>` : '<p class="muted" style="margin-bottom:1rem;">Рынки для этой страны ещё не заданы.</p>'}

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

    function levelInfo(hhi, share) {
        const L = {
            high: { label: 'Высокий', bg: '#fee2e2', color: '#b91c1c', border: '#fca5a5' },
            mid:  { label: 'Умеренный', bg: '#ffedd5', color: '#c2410c', border: '#fdba74' },
            low:  { label: 'Низкий', bg: '#dcfce7', color: '#15803d', border: '#86efac' },
        };
        if (hhi != null) return { ...(hhi > 2500 ? L.high : hhi >= 1500 ? L.mid : L.low), basis: 'HHI' };
        if (share != null) return { ...(share > 70 ? L.high : share >= 40 ? L.mid : L.low), basis: 'доле лидера' };
        return null;
    }

    function levelBadge(mk) {
        const lv = levelInfo(mk.hhi, mk.share);
        if (!lv) return '<b>—</b>';
        return `<span class="badge" title="Оценка по ${lv.basis}"
                    style="background:${lv.bg}; color:${lv.color}; border:1.5px solid ${lv.border}">${lv.label}</span>`;
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

        const params = new URLSearchParams();
        if (currentYear) params.set('year', currentYear);
        if (currentType) params.set('type', currentType);
        if (currentMarket) params.set('market', currentMarket);
        if (typeof COUNTRY_ID !== 'undefined' && COUNTRY_ID) {
            params.set('country', COUNTRY_ID);
        }

        fetch(`/api/scopes/${SCOPE}/industries/${INDUSTRY_ID}?${params.toString()}`)
            .then(r => r.json())
            .then(res => {
                const d = res.data;
                if (!d) { document.getElementById('markets-container').innerHTML = '<p class="muted">Нет данных.</p>'; return; }
                countryNotes = d.country_notes || [];
                currentIndustry = d.industry?.name || '';

                if (typeSelect && typeSelect.options.length === 1 && d.monopoly_types) {
                    d.monopoly_types.forEach(t => {
                        typeSelect.innerHTML += `<option value="${t.id}">${t.name}</option>`;
                    });
                }

                if (marketSelect && marketSelect.options.length === 1 && d.markets) {
                    d.markets.forEach(mk => {
                        marketSelect.innerHTML += `<option value="${mk.id}">${escapeHtml(mk.name)}</option>`;
                    });
                }

                renderInfo(d);
                renderFlags(d);
                renderMarkets(d);
            });
    }

    function renderInfo(d) {
        const year = d.year != null ? d.year : '';
        const count = d.companies_count != null ? d.companies_count : d.companies.length;
        const marketsCount = (d.markets || []).length;

        infoEl.innerHTML = `
            <div class="sector-cell">
                <div class="sector-value small">Компаний: ${count} · ${year}</div>
            </div>
            <div class="sector-cell">
                <div class="sector-value">${marketsCount}</div>
                <div class="sector-label">Рынков</div>
            </div>
            <div class="sector-cell">
                <div class="sector-value">${fmtMoney(d.total_revenue, d.currency)}</div>
                <div class="sector-label">Выручка отрасли</div>
            </div>
        `;
    }

    function renderFlags(d) {
        if (SCOPE !== 'ru') {
            flagsEl.innerHTML = '';
            flagsEl.style.display = 'none';
            return;
        }
        flagsEl.style.display = '';
        const notes = d.country_notes || [];
        if (!notes.length) {
            flagsEl.innerHTML = '<span class="muted">Нет данных по странам для этой отрасли.</span>';
            return;
        }
        flagsEl.innerHTML = `
            <div class="flags-label">Сравнение рынков по странам</div>
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

    function companyCard(c, i, marketId) {
        const logoSrc = c.logo_filename
            ? `/static/uploads/logos/${c.logo_filename}`
            : c.logo_url;
        const logoBlock = logoSrc
            ? `<img class="co-logo-img" src="${logoSrc}" alt="">`
            : `<div class="co-logo" style="background:${shade(c.color)}; color:${c.color || '#475569'}">${initials(c.short_name || c.name)}</div>`;
        const share = (c.share != null) ? `${c.share}%` : '—';
        const href = marketId
            ? `/company/${c.monopoly_id}?market=${marketId}`
            : `/company/${c.monopoly_id}`;
        return `
            <a href="${href}" class="company-card fade-in" style="animation-delay:${(i * 0.04)}s">
                ${logoBlock}
                <div class="co-name">${escapeHtml(c.name)}</div>
                <div class="co-metrics">
                    <div><span class="muted">Доля</span><b>${share}${c.is_main ? ' <span title="Основной рынок компании">★</span>' : ''}</b></div>
                </div>
                <div class="co-open">Открыть досье &rarr;</div>
            </a>`;
    }

    function renderMarkets(d) {
        const markets = d.markets || [];
        const container = document.getElementById('markets-container');
        if (!container) return;

        if (!markets.length) {
            const companies = d.companies || [];
            if (!companies.length) {
                container.innerHTML = '<p class="muted">Данных по отрасли пока нет.</p>';
                return;
            }
            container.innerHTML = `
                <div class="market-block">
                    <div class="market-head">
                        <span class="market-name">Компании отрасли</span>
                    </div>
                    <p class="muted" style="margin:0 0 .75rem; font-size:12px;">
                        Для этой отрасли ещё не заданы рынки — показаны все компании отрасли.
                    </p>
                    <div class="company-grid">
                        ${companies.map((c, i) => companyCard(c, i)).join('')}
                    </div>
                </div>`;
            return;
        }

        container.innerHTML = markets.map(mk => `
            <div class="market-block">
                <div class="market-head">
                    <span class="market-name">${escapeHtml(mk.name)}</span>
                    <span class="market-hhi">HHI: ${mk.hhi != null ? mk.hhi : '—'}</span>
                </div>
                ${marketMeta(mk)}
                <div class="company-grid market-companies-grid">
                    ${mk.companies.map((c, i) => companyCard(c, i, mk.id)).join('')}
                </div>
                ${mk.others > 0 ? `
                    <div class="market-others">
                        <span class="market-others-label">Остальные компании рынка</span>
                        <span class="market-others-bar"><span class="market-others-fill" style="width:${Math.min(mk.others, 100)}%"></span></span>
                        <span class="market-others-value">${mk.others}%</span>
                    </div>` : ''}
            </div>
        `).join('');
    }

    function marketMeta(mk) {
        if (!mk.monopoly_type && !mk.risks) return '';
        const b = badgeInfo(mk.monopoly_type);
        const typeHtml = mk.monopoly_type
            ? `<div class="market-type"><span class="muted">Тип монополии рынка:</span>
                 <span class="badge" style="background:${b.bg}; color:${b.color}; border:1.5px solid ${b.border}">${escapeHtml(b.label)}</span></div>`
            : '';
        const riskHtml = mk.risks
            ? `<div class="market-risks"><b>Чем грозит монополизация:</b> ${escapeHtml(mk.risks)}</div>`
            : '';
        return `<div class="market-meta">${typeHtml}${riskHtml}</div>`;
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

const CURRENCY_LABEL = {
        RUB: 'руб.', USD: 'долл.', EUR: 'евро', CNY: 'юан.', NOK: 'крон NOK', SEK: 'крон SEK',
        JPY: 'иен', KRW: 'вон', TWD: 'NT$', CHF: 'CHF', GBP: 'фунт.', SAR: 'SAR', CAD: 'CAD'
    };
    function currencyLabel(code) { return code ? (CURRENCY_LABEL[code] || code) : ''; }
    function fmtMoney(v, cur) {
        if (v == null) return '—';
        return v.toLocaleString('ru-RU') + ' млн' + (cur ? ' ' + currencyLabel(cur) : '');
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

    if (marketSelect) {
        marketSelect.addEventListener('change', () => {
            currentMarket = marketSelect.value ? Number(marketSelect.value) : null;
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
