document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('monopolies-container');
    const filterCountry = document.getElementById('filter-country');
    const filterType = document.getElementById('filter-type');
    const filterIndustry = document.getElementById('filter-industry');
    const filterQ = document.getElementById('filter-q');
    const form = document.getElementById('filters-form');
    const resetBtn = document.getElementById('filters-reset');

    // Загрузка справочников
    fetch('/api/countries')
        .then(r => r.json())
        .then(res => {
            (res.data || []).forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.id;
                opt.textContent = c.name;
                filterCountry.appendChild(opt);
            });
        });

    fetch('/api/industries')
        .then(r => r.json())
        .then(res => {
            (res.data || []).forEach(i => {
                const opt = document.createElement('option');
                opt.value = i.id;
                opt.textContent = i.name;
                filterIndustry.appendChild(opt);
            });
        });

    function loadMonopolies() {
        container.innerHTML = '<p class="muted">Загрузка...</p>';

        const params = new URLSearchParams();
        if (filterCountry.value) params.set('country', filterCountry.value);
        if (filterType.value) params.set('type', filterType.value);
        if (filterIndustry.value) params.set('industry', filterIndustry.value);
        if (filterQ.value.trim()) params.set('q', filterQ.value.trim());

        fetch('/api/monopolies?' + params.toString())
            .then(r => r.json())
            .then(res => {
                const items = res.data || [];
                if (!items.length) {
                    container.innerHTML = '<p class="muted">Ничего не найдено.</p>';
                    return;
                }

                const grouped = {};
                items.forEach(m => {
                    const key = `${m.country.name} — ${m.industry.name}`;
                    if (!grouped[key]) grouped[key] = [];
                    grouped[key].push(m);
                });

                let html = '';
                for (const [group, list] of Object.entries(grouped)) {
                    html += `<section class="industry"><h2>${escapeHtml(group)}</h2><div class="cards">`;
                    list.forEach(m => {
                        const type = (m.monopoly_type || '').toLowerCase().trim();
                        const label = type === 'natural' ? 'Естественная' : 'Искусственная';
                        html += `
                            <a href="/monopoly/${m.id}" class="card fade-in">
                                <h3>${escapeHtml(m.name)}</h3>
                                <p class="muted">ИНН: ${escapeHtml(m.inn)}</p>
                                <span class="badge badge-${type}">${label}</span>
                            </a>`;
                    });
                    html += '</div></section>';
                }
                container.innerHTML = html;
            })
            .catch(err => {
                container.innerHTML = `<p class="muted">Ошибка загрузки: ${err.message}</p>`;
            });
    }

    form.addEventListener('submit', e => {
        e.preventDefault();
        loadMonopolies();
    });

    resetBtn.addEventListener('click', () => {
        filterCountry.value = '';
        filterType.value = '';
        filterIndustry.value = '';
        filterQ.value = '';
        loadMonopolies();
    });

    loadMonopolies();

    function escapeHtml(s) {
        return String(s).replace(/[&<>"']/g, c => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;',
            '"': '&quot;', "'": '&#39;'
        }[c]));
    }
});