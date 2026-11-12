document.addEventListener('DOMContentLoaded', () => {
    Promise.all([
        fetch('/api/scopes/world/totals').then(r => r.json()),
        fetch('/api/scopes/ru/totals').then(r => r.json()),
    ]).then(([world, ru]) => {
        renderStats('stats-world', world.data);
        renderStats('stats-ru', ru.data);

        const totalsEl = document.getElementById('dash-totals');
        const w = world.data || {};
        const r = ru.data || {};

        const sectorsCount = (w.sectors || 0) + (r.sectors || 0);
        const companiesCount = (w.companies || 0) + (r.companies || 0);
        const maxShare = Math.max(w.max_share || 0, r.max_share || 0);
        const countriesCount = (w.countries || 0) + (r.countries || 0);

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