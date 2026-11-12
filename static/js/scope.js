document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('bars-container');
    const yearSelect = document.getElementById('year-select');
    let currentYear = null;

    function barColor(share) {
        if (share > 70) return 'linear-gradient(90deg,#dc2626,#ef4444)';
        if (share > 40) return 'linear-gradient(90deg,#ea580c,#f97316)';
        return 'linear-gradient(90deg,#16a34a,#22c55e)';
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
        
        // Если мы внутри страны, передаем ID
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
                
                container.innerHTML = '';
                d.sectors.forEach(s => {
                    const row = document.createElement('a');
                    row.className = 'bar-row';
                    
                    // Передаем country в ссылку на отрасль
                    const industryUrl = `/scope/${SCOPE}/industry/${s.id}${COUNTRY_ID ? '?country=' + COUNTRY_ID : ''}`;
                    row.href = industryUrl;
                    
                    row.innerHTML = `
                        <div class="bar-row-head">
                            <span class="bar-name">${escapeHtml(s.name)}</span>
                            <span class="bar-metric">HHI: ${s.hhi != null ? s.hhi : '—'}</span>
                            <span class="bar-share">${s.top_share.toFixed(1)}%</span>
                        </div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width:${s.top_share}%; background:${barColor(s.top_share)}">
                                ${s.top_share > 15 ? s.top_share.toFixed(1) + '%' : ''}
                            </div>
                        </div>
                        <div class="bar-sub muted">${s.companies_count} компан. · выручка ${fmtMoney(s.total_revenue)}</div>
                    `;
                    container.appendChild(row);
                });
            });
    }

    yearSelect.addEventListener('change', () => {
        currentYear = yearSelect.value ? Number(yearSelect.value) : null;
        load();
    });

    loadYears().then(load);

    function fmtMoney(v) {
        if (v == null) return '—';
        return v.toLocaleString('ru-RU') + ' млн';
    }
    function escapeHtml(s) {
        return String(s).replace(/[&<>"']/g, c => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
        }[c]));
    }
});