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

        fetch(`/api/scopes/${SCOPE}?${params.toString()}`)
            .then(r => r.json())
            .then(res => {
                const d = res.data;
                const sectors = (d.sectors || []).slice();
                if (!sectors.length) {
                    container.innerHTML = '<p class="muted">Нет данных.</p>';
                    return;
                }
                container.innerHTML = '';
                sectors.forEach((s, i) => {
                    const row = document.createElement('a');
                    row.className = 'bar-row fade-in';
                    row.href = `/scope/${SCOPE}/industry/${s.id}`;
                    row.style.animationDelay = (i * 0.05) + 's';
                    row.innerHTML = `
                        <div class="bar-row-head">
                            <span class="bar-name">${escapeHtml(s.name)}</span>
                            <span class="bar-metric">HHI: ${s.hhi != null ? s.hhi : '—'}</span>
                            <span class="bar-share">${s.top_share.toFixed(1)}%</span>
                        </div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width:0%; background:${barColor(s.top_share)}">
                                ${s.top_share > 15 ? s.top_share.toFixed(1) + '%' : ''}
                            </div>
                        </div>
                        <div class="bar-sub muted">${s.companies_count} компан. · выручка ${fmtMoney(s.total_revenue)}</div>
                    `;
                    container.appendChild(row);
                    setTimeout(() => {
                        row.querySelector('.bar-fill').style.width = s.top_share + '%';
                    }, 60 + i * 90);
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
            '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
        }[c]));
    }
});