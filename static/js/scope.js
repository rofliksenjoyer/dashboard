document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('industries-container');
    const yearSelect = document.getElementById('year-select');
    let currentYear = null;

    function industryHref(id) {
        return `/scope/${SCOPE}/industry/${id}${COUNTRY_ID ? '?country=' + COUNTRY_ID : ''}`;
    }

    function companiesLabel(n) {
        const mod10 = n % 10;
        const mod100 = n % 100;
        if (mod10 === 1 && mod100 !== 11) return 'компания';
        if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return 'компании';
        return 'компаний';
    }

    function renderSectors(sectors) {
        container.innerHTML = '<ul class="industry-list">' + sectors.map(s => {
            const markets = s.markets || [];
            const marketsHtml = markets.length
                ? `<ul class="industry-markets">
                       ${markets.map(mk => `
                           <li>
                               <span class="mk-name">${escapeHtml(mk.name)}</span>
                               <span class="mk-hhi">HHI ${mk.hhi != null ? Math.round(mk.hhi) : '—'}</span>
                           </li>
                       `).join('')}
                   </ul>`
                : '<p class="industry-empty muted">Рынки не указаны</p>';

            return `
                <li class="industry-item">
                    <a class="industry-link" href="${industryHref(s.id)}">
                        <span class="industry-name">${escapeHtml(s.name)}</span>
                        <span class="industry-meta">
                            <span>${s.companies_count} ${companiesLabel(s.companies_count)}</span>
                            <span>Общая выручка: <b>${fmtMoney(s.total_revenue, s.currency)}</b></span>
                        </span>
                        ${marketsHtml}
                    </a>
                </li>
            `;
        }).join('') + '</ul>';
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
        container.innerHTML = '<p class="muted">Загрузка…</p>';
        const params = new URLSearchParams();
        if (currentYear) params.set('year', currentYear);

        if (typeof COUNTRY_ID !== 'undefined' && COUNTRY_ID) {
            params.set('country', COUNTRY_ID);
        }

        fetch(`/api/scopes/${SCOPE}?${params.toString()}`)
            .then(r => r.json())
            .then(res => {
                const d = res.data;

                if (d.type === "countries") {
                    container.innerHTML = `<div class="company-grid">` + d.data.map(c => `
                        <a href="/scope/ru?country=${c.id}" class="company-card fade-in">
                            <div class="co-logo">${c.flag_emoji || c.code}</div>
                            <div class="co-name">${c.name}</div>
                            <div class="co-open">Выбрать &rarr;</div>
                        </a>
                    `).join('') + `</div>`;
                    return;
                }

                if (!d.sectors || !d.sectors.length) {
                    container.innerHTML = '<p class="muted">Нет данных.</p>';
                    return;
                }

                renderSectors(d.sectors);
            });
    }

    yearSelect.addEventListener('change', () => {
        currentYear = yearSelect.value ? Number(yearSelect.value) : null;
        load();
    });

    loadYears().then(load);

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
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
        }[c]));
    }
});
