document.addEventListener('DOMContentLoaded', () => {
    Promise.all([
        fetch('/api/scopes/world/totals').then(r => r.json()),
        fetch('/api/scopes/ru/totals').then(r => r.json()),
        fetch('/api/totals').then(r => r.json()),
    ]).then(([world, ru, all]) => {
        renderStats('stats-world', world.data);
        renderStats('stats-ru', ru.data);

        const totalsEl = document.getElementById('dash-totals');
        const t = all.data || {};
        const sectorsCount = t.sectors || 0;
        const companiesCount = t.companies || 0;
        const maxShare = t.max_share || 0;
        const countriesCount = t.countries || 0;

        totalsEl.innerHTML = `
            <div class="stat-box">
                <div class="stat-num text-indigo">${countriesCount}</div>
                <div class="stat-label">Стран в базе</div>
            </div>
            <div class="stat-box">
                <div class="stat-num text-violet">${sectorsCount}</div>
                <div class="stat-label">Отраслей</div>
            </div>
            <div class="stat-box">
                <div class="stat-num text-emerald">${companiesCount}</div>
                <div class="stat-label">Компаний-лидеров</div>
            </div>
            <div class="stat-box">
                <div class="stat-num text-rose">${Math.round(maxShare)}%</div>
                <div class="stat-label">Макс. монополизация</div>
            </div>
        `;
    });

    function renderStats(elId, d) {
        const el = document.getElementById(elId);
        if (!el || !d) { if (el) el.textContent = '—'; return; }
        el.innerHTML = `
            <span class="pill">${d.sectors || 0} отрасл.</span>
            <span class="pill">${d.companies || 0} компан.</span>
            <span class="pill">Макс. ${Math.round(d.max_share || 0)}%</span>
        `;
    }
});
