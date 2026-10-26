"""
Уровни анализа:
1. Контур (market_scope: world / ru) -> рейтинг отраслей
2. Отрасль в контуре -> HHI, доли рынка, компании, заметки по странам
3. Компания (монополия) -> паспорт + метрики
"""
from extensions import db
from models import (
    Country, Industry, MonopolyType, Monopoly, Period, PeriodValue, Metric,
    CountryIndustryNote,
)


VALID_SCOPES = ("ru", "world")

INFO_METRIC_CODES = (
    "personnel_costs", "amortization",
    "operating_loss", "financial_income", "financial_expenses",
)

TABLE_METRIC_CODES = (
    ("revenue",           "Выручка от продаж"),
    ("net_profit",        "Чистая прибыль (убыток)"),
    ("assets",            "Активы"),
    ("equity",            "Собственный капитал"),
    ("credits",           "Кредиты и займы"),
    ("personnel_costs",   "Затраты на персонал"),
    ("amortization",      "Амортизация"),
    ("operating_loss",    "Убыток от операционной деятельности"),
    ("financial_income",  "Финансовые доходы"),
    ("financial_expenses","Финансовые расходы"),
)


def get_metric_value(period, code):
    m = Metric.query.filter_by(code=code).first()
    if not m:
        return None
    v = PeriodValue.query.filter_by(period_id=period.id, metric_id=m.id).first()
    return float(v.value) if v else None


def get_metric_values_map(period):
    return {pv.metric.code: float(pv.value) for pv in period.values}


def available_years():
    rows = db.session.query(Period.year).distinct().order_by(Period.year).all()
    return [r[0] for r in rows]


def _period_for(monopoly_id, year):
    return Period.query.filter_by(monopoly_id=monopoly_id, year=year).first()


def _countries_for_scope(scope):
    return (
        Country.query
        .filter_by(market_scope=scope)
        .order_by(Country.name)
        .all()
    )


def calculate_market_shares(country_id, industry_id, year):
    monopolies = Monopoly.query.filter_by(
        country_id=country_id, industry_id=industry_id
    ).all()

    rows = []
    for m in monopolies:
        period = _period_for(m.id, year)
        if not period:
            continue
        revenue = get_metric_value(period, "revenue")
        if revenue:
            rows.append({
                "monopoly_id": m.id,
                "name": m.name,
                "short_name": m.short_name or m.name,
                "color": m.color,
                "revenue": revenue,
            })

    total = sum(r["revenue"] for r in rows)
    if not total:
        return []

    for r in rows:
        r["share"] = round(r["revenue"] / total * 100, 2)
        r["revenue"] = round(r["revenue"], 2)

    rows.sort(key=lambda r: r["revenue"], reverse=True)
    return rows


def calculate_hhi(country_id, industry_id, year):
    shares = calculate_market_shares(country_id, industry_id, year)
    if not shares:
        return None
    return round(sum(s["share"] ** 2 for s in shares), 2)


def _hhi_for_scope(scope, industry_id, year):
    countries = _countries_for_scope(scope)
    shares = []
    for c in countries:
        shares.extend(calculate_market_shares(c.id, industry_id, year))
    if not shares:
        return None
    total = sum(x["revenue"] for x in shares)
    if not total:
        return None
    for x in shares:
        x["share"] = round(x["revenue"] / total * 100, 2)
    return round(sum(x["share"] ** 2 for x in shares), 2)


def get_scope_overview(scope, year=None):
    if scope not in VALID_SCOPES:
        return None

    if year is None:
        years = available_years()
        year = years[-1] if years else None

    countries = _countries_for_scope(scope)
    country_ids = [c.id for c in countries]
    if not country_ids:
        return {
            "scope": scope, "year": year, "sectors": [],
            "totals": {"sectors": 0, "companies": 0, "max_share": 0,
                       "total_revenue": 0, "countries": 0},
        }

    industries = (
        Industry.query
        .join(Monopoly, Monopoly.industry_id == Industry.id)
        .filter(Monopoly.country_id.in_(country_ids))
        .distinct()
        .order_by(Industry.name)
        .all()
    )

    sectors = []
    total_companies = 0
    total_revenue = 0.0
    max_share = 0.0

    for ind in industries:
        shares = []
        for cid in country_ids:
            shares.extend(calculate_market_shares(cid, ind.id, year))

        top = 0.0
        hhi_val = None
        rev_sum = 0.0

        if shares:
            total = sum(x["revenue"] for x in shares)
            if total:
                for x in shares:
                    x["share"] = round(x["revenue"] / total * 100, 2)
                shares.sort(key=lambda r: r["revenue"], reverse=True)
                hhi_val = round(sum(x["share"] ** 2 for x in shares), 2)
                rev_sum = total
                top = shares[0]["share"]
                max_share = max(max_share, top)

        present_countries = []
        country_ids_with_data = set()

        for c in countries:
            own = calculate_market_shares(c.id, ind.id, year)
            if own:
                country_ids_with_data.add(c.id)

        all_notes = CountryIndustryNote.query.filter_by(industry_id=ind.id).all()
        for note in all_notes:
            country_ids_with_data.add(note.country_id)

        all_countries = Country.query.all()
        c_map = {c.id: c for c in all_countries}

        for cid in country_ids_with_data:
            c = c_map.get(cid)
            if not c:
                continue
            note = CountryIndustryNote.query.filter_by(
                country_id=c.id, industry_id=ind.id
            ).first()
            present_countries.append({
                "country_id": c.id,
                "country_name": c.name,
                "country_code": c.code,
                "country_flag": c.flag_emoji,
                "has_note": bool(note and note.body and note.body.strip()),
            })

        sectors.append({
            "id": ind.id,
            "name": ind.name,
            "companies_count": len(shares),
            "top_share": top,
            "hhi": hhi_val,
            "total_revenue": round(rev_sum, 2),
            "countries": present_countries,
        })
        total_companies += len(shares)
        total_revenue += rev_sum

    sectors.sort(key=lambda x: x["top_share"], reverse=True)

    return {
        "scope": scope,
        "year": year,
        "sectors": sectors,
        "totals": {
            "sectors": len(sectors),
            "companies": total_companies,
            "max_share": round(max_share, 2),
            "total_revenue": round(total_revenue, 2),
            "countries": len(countries),
        },
    }


def get_sector_detail(scope, industry_id, year=None):
    if scope not in VALID_SCOPES:
        return None

    years = available_years()
    if year is None:
        year = years[-1] if years else None

    industry = Industry.query.get(industry_id)
    if not industry:
        return None

    countries = _countries_for_scope(scope)
    shares = []
    for c in countries:
        shares.extend(calculate_market_shares(c.id, industry_id, year))

    for row in shares:
        m = Monopoly.query.get(row["monopoly_id"])
        if m:
            row["country_id"] = m.country_id
            row["country_name"] = m.country.name
            row["country_code"] = m.country.code
            row["country_flag"] = m.country.flag_emoji
            row["logo_url"] = m.logo_url
            row["logo_filename"] = m.logo_filename
            row["monopoly_type"] = m.monopoly_type.name if m.monopoly_type else None

    if not shares:
        return {
            "industry": {"id": industry.id, "name": industry.name},
            "scope": scope,
            "year": year,
            "companies": [],
            "hhi": None,
            "hhi_dynamics": [{"year": y, "hhi": None} for y in years],
            "total_revenue": 0,
            "top_share": 0,
            "country_notes": [],
        }

    total = sum(x["revenue"] for x in shares)
    if total:
        for x in shares:
            x["share"] = round(x["revenue"] / total * 100, 2)
    shares.sort(key=lambda r: r["revenue"], reverse=True)
    hhi_val = round(sum(x["share"] ** 2 for x in shares), 2)

    hhi_dynamics = []
    for y in years:
        hhi_dynamics.append({
            "year": y,
            "hhi": _hhi_for_scope(scope, industry_id, y),
        })

    notes = []
    country_ids_with_data = set()
    for c in countries:
        own = calculate_market_shares(c.id, industry_id, year)
        if own:
            country_ids_with_data.add(c.id)

    all_notes = CountryIndustryNote.query.filter_by(industry_id=industry_id).all()
    for note in all_notes:
        country_ids_with_data.add(note.country_id)

    all_countries = Country.query.all()
    c_map = {c.id: c for c in all_countries}

    for cid in country_ids_with_data:
        c = c_map.get(cid)
        if not c:
            continue
        note = CountryIndustryNote.query.filter_by(
            country_id=c.id, industry_id=industry_id
        ).first()
        own = calculate_market_shares(c.id, industry_id, year)

        top_companies = [
            {"name": x["short_name"] or x["name"], "share": x["share"]}
            for x in own[:3]
        ]
        notes.append({
            "country_id": c.id,
            "country_name": c.name,
            "country_code": c.code,
            "country_flag": c.flag_emoji,
            "title": (note.title if note else None) or c.name,
            "body": note.body if note else None,
            "hhi": (note.hhi_override if note and note.hhi_override is not None
                    else calculate_hhi(c.id, industry_id, year)),
            "top_share": (note.top_share_override if note and note.top_share_override is not None
                          else (own[0]["share"] if own else 0)),
            "companies_count": (note.companies_override if note and note.companies_override is not None
                                else len(own)),
            "top_companies": top_companies,
        })

    return {
        "industry": {"id": industry.id, "name": industry.name},
        "scope": scope,
        "year": year,
        "companies": shares,
        "hhi": hhi_val,
        "hhi_dynamics": hhi_dynamics,
        "total_revenue": round(total, 2),
        "top_share": shares[0]["share"],
        "country_notes": notes,
    }


def calculate_ratios_for_period(period):
    revenue = get_metric_value(period, "revenue")
    net_profit = get_metric_value(period, "net_profit")
    assets = get_metric_value(period, "assets")
    equity = get_metric_value(period, "equity")
    credits = get_metric_value(period, "credits")

    ratios = {}
    try:
        if revenue and net_profit is not None:
            ratios["profitability"] = round(net_profit / revenue * 100, 2)
        if equity and net_profit is not None:
            ratios["roe"] = round(net_profit / equity * 100, 2)
        if assets and equity:
            ratios["autonomy"] = round(equity / assets, 2)
        if equity and credits:
            ratios["debt_load"] = round(credits / equity, 2)
    except ZeroDivisionError:
        pass
    return ratios


def calculate_growth_rates(periods):
    result = []
    prev_rev = prev_profit = None
    for p in periods:
        revenue = get_metric_value(p, "revenue")
        profit = get_metric_value(p, "net_profit")
        row = {"year": p.year, "revenue_growth": None, "profit_growth": None}
        if prev_rev and revenue is not None and prev_rev != 0:
            row["revenue_growth"] = round((revenue - prev_rev) / abs(prev_rev) * 100, 2)
        if prev_profit and profit is not None and prev_profit != 0:
            row["profit_growth"] = round((profit - prev_profit) / abs(prev_profit) * 100, 2)
        result.append(row)
        prev_rev, prev_profit = revenue, profit
    return result


def get_company_passport(monopoly_id):
    m = Monopoly.query.get(monopoly_id)
    if not m:
        return None

    periods = (
        Period.query.filter_by(monopoly_id=monopoly_id)
        .order_by(Period.year).all()
    )

    periods_data = []
    for p in periods:
        values = {}
        for pv in p.values:
            values[pv.metric.code] = {
                "name": pv.metric.name,
                "unit": pv.metric.unit,
                "value": float(pv.value),
            }
        table = {}
        for code, _label in TABLE_METRIC_CODES:
            table[code] = values.get(code, {}).get("value")

        periods_data.append({
            "year": p.year,
            "values": values,
            "ratios": calculate_ratios_for_period(p),
            "table": table,
        })

    court_cases = [
        {
            "id": c.id,
            "case_number": c.case_number,
            "court_name": c.court_name,
            "decision_date": c.decision_date.isoformat() if c.decision_date else None,
            "decision_link": c.decision_link,
            "summary": c.summary,
            "status": c.status,
        }
        for c in m.court_cases
    ]

    return {
        "id": m.id,
        "name": m.name,
        "short_name": m.short_name,
        "inn": m.inn,
        "color": m.color,
        "logo_url": m.logo_url,
        "logo_filename": m.logo_filename,
        "monopoly_type": m.monopoly_type.name if m.monopoly_type else None,
        "description": m.description,
        "activity": m.activity,
        "website": m.website,
        "employees": m.employees,
        "founded_year": m.founded_year,
        "hq": m.hq,
        "industry": {"id": m.industry.id, "name": m.industry.name},
        "country": {
            "id": m.country.id,
            "name": m.country.name,
            "code": m.country.code,
            "market_scope": m.country.market_scope,
            "flag_emoji": m.country.flag_emoji,
        },
        "periods": periods_data,
        "growth_rates": calculate_growth_rates(periods),
        "court_cases": court_cases,
        "table_columns": [
            {"code": code, "label": label}
            for code, label in TABLE_METRIC_CODES
        ],
    }


def get_info_metrics(monopoly_id, year=None):
    if year is None:
        periods = (
            Period.query.filter_by(monopoly_id=monopoly_id)
            .order_by(Period.year.desc()).all()
        )
        if not periods:
            return {"year": None, "items": []}
        period = periods[0]
    else:
        period = Period.query.filter_by(
            monopoly_id=monopoly_id, year=year
        ).first()
        if not period:
            return {"year": year, "items": []}

    values_map = get_metric_values_map(period)
    items = []
    for code in INFO_METRIC_CODES:
        metric = Metric.query.filter_by(code=code).first()
        if not metric:
            continue
        items.append({
            "code": code,
            "name": metric.name,
            "unit": metric.unit,
            "value": values_map.get(code),
        })
    return {"year": period.year, "items": items}