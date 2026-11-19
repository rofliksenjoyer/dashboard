from collections import defaultdict
from extensions import db
from models import (
    Country, Industry, MonopolyType, Monopoly, Period, PeriodValue, Metric,
    CountryIndustryNote, Market, MonopolyMarket,
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
    ("liabilities",       "Обязательства"),
    ("personnel_costs",   "Затраты на персонал"),
    ("amortization",      "Амортизация"),
    ("operating_loss",    "Убыток от операционной деятельности"),
    ("financial_income",  "Финансовые доходы"),
    ("financial_expenses","Финансовые расходы"),
)


def currency_of(m):
    if m.market_scope == "world":
        return "USD"
    return m.country.currency if m.country else None


def _common_currency(monopolies):
    cur = {currency_of(m) for m in monopolies}
    return cur.pop() if len(cur) == 1 else None


def get_metric_value(period, code):
    m = Metric.query.filter_by(code=code).first()
    if not m:
        return None
    v = PeriodValue.query.filter_by(period_id=period.id, metric_id=m.id).first()
    return float(v.value) if v else None


def liabilities_for(values):
    assets, equity = values.get("assets"), values.get("equity")
    if assets is not None and equity is not None:
        return round(assets - equity, 2), "calc"
    if values.get("credits") is not None:
        return values["credits"], "credits"
    return None, None


def get_metric_values_map(period):
    return {pv.metric.code: float(pv.value) for pv in period.values}


def available_years():
    rows = db.session.query(Period.year).distinct().order_by(Period.year).all()
    return [r[0] for r in rows]


def _period_for(monopoly_id, year):
    p = Period.query.filter_by(monopoly_id=monopoly_id, year=year).first()
    if p or year is None:
        return p
    return (
        Period.query.filter(Period.monopoly_id == monopoly_id, Period.year < year)
        .order_by(Period.year.desc()).first()
    )


def _markets_for(scope, industry_id, country_id=None):
    q = Market.query.filter_by(industry_id=industry_id, market_scope=scope)
    if country_id is not None:
        q = q.filter_by(country_id=country_id)
    else:
        q = q.filter(Market.country_id.is_(None))
    return q.order_by(Market.name).all()


def _company_main_entry(monopoly_id):
    entries = MonopolyMarket.query.filter_by(monopoly_id=monopoly_id).all()
    if not entries:
        return None
    for e in entries:
        if e.is_main:
            return e
    return max(entries, key=lambda x: (x.share if x.share is not None else -1))


def _market_to_dict(market):
    entries = MonopolyMarket.query.filter_by(market_id=market.id).all()
    companies = []
    total = 0.0
    for e in entries:
        m = e.monopoly
        companies.append({
            "monopoly_id": m.id,
            "name": m.name,
            "short_name": m.short_name or m.name,
            "color": m.color,
            "logo_url": m.logo_url,
            "logo_filename": m.logo_filename,
            "share": round(float(e.share), 2),
            "is_main": bool(e.is_main),
            "country_id": m.country_id,
            "country_name": m.country.name,
            "country_code": m.country.code,
            "country_flag": m.country.flag_emoji,
        })
        total += float(e.share)
    companies.sort(key=lambda x: x["share"], reverse=True)
    others = round(max(0.0, 100.0 - total), 2)
    return {
        "id": market.id,
        "name": market.name,
        "hhi": market.hhi,
        "country_id": market.country_id,
        "monopoly_type": market.monopoly_type.name if market.monopoly_type else None,
        "risks": market.risks,
        "companies": companies,
        "others": others,
    }


def get_market_detail(market_id):
    market = Market.query.get(market_id)
    if not market:
        return None
    d = _market_to_dict(market)
    d["industry"] = (
        {"id": market.industry_id, "name": market.industry.name}
        if market.industry else None
    )
    d["scope"] = market.market_scope
    return d


def _market_summary(market):
    return {
        "id": market.id,
        "name": market.name,
        "hhi": market.hhi,
    }


def _industry_top_share_and_hhi(scope, industry_id, country_id=None):
    top = 0.0
    hhi = None
    for market in _markets_for(scope, industry_id, country_id):
        for e in MonopolyMarket.query.filter_by(market_id=market.id).all():
            m = e.monopoly
            if country_id is not None and m.country_id != country_id:
                continue
            if e.share is not None:
                top = max(top, float(e.share))
        if market.hhi is not None:
            hhi = market.hhi if hhi is None else max(hhi, market.hhi)
    return round(top, 2), hhi


def _participants_count(scope, industry_id, country_id=None, fallback=0):
    ids = set()
    for mk in _markets_for(scope, industry_id, country_id):
        for e in MonopolyMarket.query.filter_by(market_id=mk.id).all():
            if e.share is not None:
                ids.add(e.monopoly_id)
    return len(ids) if ids else fallback


def _company_rows(scope, industry_id, country_id=None, market_id=None):
    query = Monopoly.query.filter_by(market_scope=scope, industry_id=industry_id)
    if country_id:
        query = query.filter_by(country_id=country_id)
    if market_id:
        query = query.join(
            MonopolyMarket, MonopolyMarket.monopoly_id == Monopoly.id
        ).filter(MonopolyMarket.market_id == market_id)

    rows = []
    for m in query.all():
        if market_id:
            e = MonopolyMarket.query.filter_by(
                monopoly_id=m.id, market_id=market_id
            ).first()
        else:
            e = _company_main_entry(m.id)
        rows.append({
            "monopoly_id": m.id,
            "name": m.name,
            "short_name": m.short_name or m.name,
            "color": m.color,
            "logo_url": m.logo_url,
            "logo_filename": m.logo_filename,
            "country_id": m.country_id,
            "country_name": m.country.name,
            "country_code": m.country.code,
            "country_flag": m.country.flag_emoji,
            "currency": currency_of(m),
            "share": round(float(e.share), 2) if (e and e.share is not None) else None,
            "market_name": e.market.name if e else None,
        })
    rows.sort(key=lambda x: (x["share"] is None, -(x["share"] or 0)))
    return rows


def get_global_totals(scope):
    companies = Monopoly.query.filter_by(market_scope=scope).all()
    industries_count = len({m.industry_id for m in companies})

    years = available_years()
    year = years[-1] if years else None

    total_revenue = 0.0
    max_share = 0.0
    totals_currency = _common_currency(companies)

    for m in companies:
        if year:
            period = _period_for(m.id, year)
            if period:
                rev = get_metric_value(period, "revenue")
                if rev:
                    total_revenue += rev
        e = _company_main_entry(m.id)
        if e and e.share is not None:
            max_share = max(max_share, float(e.share))

    return {
        "sectors": industries_count,
        "companies": len(companies),
        "max_share": round(max_share, 2),
        "total_revenue": round(total_revenue, 2) if totals_currency else None,
        "currency": totals_currency,
        "countries": len({m.country_id for m in companies})
    }


def get_overall_totals():
    companies = Monopoly.query.all()
    max_share = 0.0
    for m in companies:
        e = _company_main_entry(m.id)
        if e and e.share is not None:
            max_share = max(max_share, float(e.share))
    return {
        "countries": len({m.country_id for m in companies}),
        "sectors": len({m.industry_id for m in companies}),
        "companies": len(companies),
        "max_share": round(max_share, 2),
    }


def get_scope_overview(scope, country_id=None, year=None):
    if scope not in VALID_SCOPES:
        return None

    if scope == "ru" and not country_id:
        countries = (
            db.session.query(Country)
            .join(Monopoly)
            .filter(Monopoly.market_scope == "ru")
            .distinct()
            .order_by(Country.name)
            .all()
        )
        return {
            "type": "countries",
            "data": [
                {"id": c.id, "name": c.name, "code": c.code, "flag_emoji": c.flag_emoji}
                for c in countries
            ]
        }

    if year is None:
        years = available_years()
        year = years[-1] if years else None

    query = Monopoly.query.filter_by(market_scope=scope)
    if country_id:
        query = query.filter_by(country_id=country_id)
    companies = query.all()

    industry_ids = {m.industry_id for m in companies}
    industries = (
        Industry.query
        .filter(Industry.id.in_(industry_ids))
        .order_by(Industry.name)
        .all()
    )

    sectors = []
    total_companies = 0
    total_revenue = 0.0
    total_markets = 0
    max_share = 0.0

    for ind in industries:
        ind_companies = [m for m in companies if m.industry_id == ind.id]
        companies_count = _participants_count(scope, ind.id, country_id, len(ind_companies))
        total_companies += companies_count

        rev_sum = 0.0
        for m in ind_companies:
            period = _period_for(m.id, year)
            if period:
                rev = get_metric_value(period, "revenue")
                if rev:
                    rev_sum += rev

        top, hhi = _industry_top_share_and_hhi(scope, ind.id, country_id)
        max_share = max(max_share, top)

        markets = [
            _market_summary(mk)
            for mk in _markets_for(scope, ind.id, country_id)
        ]
        total_markets += len(markets)

        sectors.append({
            "id": ind.id,
            "name": ind.name,
            "companies_count": companies_count,
            "top_share": top,
            "hhi": hhi,
            "currency": _common_currency(ind_companies),
            "total_revenue": round(rev_sum, 2) if _common_currency(ind_companies) else None,
            "markets": markets,
        })
        total_revenue += rev_sum

    sectors.sort(key=lambda x: x["top_share"], reverse=True)

    return {
        "type": "sectors",
        "scope": scope,
        "year": year,
        "sectors": sectors,
        "totals": {
            "sectors": len(sectors),
            "markets": total_markets,
            "companies": total_companies,
            "max_share": round(max_share, 2),
            "total_revenue": round(total_revenue, 2),
        },
    }


def get_sector_detail(scope, industry_id, country_id=None, type_id=None, market_id=None, year=None):
    if scope not in VALID_SCOPES:
        return None

    years = available_years()
    if year is None:
        year = years[-1] if years else None

    industry = Industry.query.get(industry_id)
    if not industry:
        return None

    company_rows = _company_rows(scope, industry_id, country_id, market_id)

    total_revenue = 0.0
    for row in company_rows:
        period = _period_for(row["monopoly_id"], year)
        if period:
            rev = get_metric_value(period, "revenue")
            row["revenue"] = round(rev, 2) if rev else None
            if rev:
                total_revenue += rev
        else:
            row["revenue"] = None

    market_objs = _markets_for(scope, industry_id, country_id)
    if type_id is not None:
        market_objs = [m for m in market_objs if m.monopoly_type_id == type_id]
    markets = [_market_to_dict(m) for m in market_objs]
    markets = [m for m in markets if m["companies"]]
    if market_id is not None:
        markets = [m for m in markets if m["id"] == market_id]

    top_share = max(
        (c["share"] for mk in markets for c in mk["companies"] if c["share"] is not None),
        default=0.0,
    )

    notes = []
    if scope == "ru":
        c_map = {c.id: c for c in Country.query.all()}
        country_ids = {
            m.country_id for m in Monopoly.query.filter_by(
                market_scope=scope, industry_id=industry_id
            ).all()
        }

        for cid in country_ids:
            c = c_map.get(cid)
            if not c:
                continue
            note = CountryIndustryNote.query.filter_by(
                country_id=c.id, industry_id=industry_id, market_scope=scope
            ).first()

            market_stats = []
            for mk in _markets_for(scope, industry_id, c.id):
                entries = [
                    e for e in MonopolyMarket.query.filter_by(market_id=mk.id).all()
                    if e.share is not None
                ]
                if not entries:
                    continue
                top = max(entries, key=lambda e: float(e.share))
                market_stats.append({
                    "market": mk.name,
                    "leader": top.monopoly.short_name or top.monopoly.name,
                    "share": round(float(top.share), 2),
                    "hhi": round(float(mk.hhi), 2) if mk.hhi is not None else None,
                })
            market_stats.sort(key=lambda x: x["share"], reverse=True)

            notes.append({
                "country_id": c.id,
                "country_name": c.name,
                "country_code": c.code,
                "country_flag": c.flag_emoji,
                "title": (note.title if note else None) or c.name,
                "body": note.body if note else None,
                "markets": market_stats,
            })

    shown_ids = {c["monopoly_id"] for mk in markets for c in mk["companies"]}
    companies_count = len(shown_ids) if markets else len(company_rows)

    sector_currency = (
        {r["currency"] for r in company_rows}.pop()
        if len({r["currency"] for r in company_rows}) == 1 else None
    )
    return {
        "industry": {"id": industry.id, "name": industry.name},
        "scope": scope,
        "year": year,
        "companies": company_rows,
        "companies_count": companies_count,
        "markets": markets,
        "top_share": round(top_share, 2),
        "total_revenue": round(total_revenue, 2) if sector_currency else None,
        "currency": sector_currency,
        "country_notes": notes,
        "monopoly_types": [{"id": t.id, "name": t.name} for t in MonopolyType.query.all()]
    }


def calculate_ratios_for_period(period):
    vals = get_metric_values_map(period)
    revenue, net_profit = vals.get("revenue"), vals.get("net_profit")
    assets, equity = vals.get("assets"), vals.get("equity")
    liabilities, basis = liabilities_for(vals)

    ratios = {}
    try:
        if revenue and net_profit is not None:
            ratios["profitability"] = round(net_profit / revenue * 100, 2)
        if equity and net_profit is not None:
            ratios["roe"] = round(net_profit / equity * 100, 2)
        if assets and equity:
            ratios["autonomy"] = round(equity / assets, 2)
        if equity and equity > 0 and liabilities is not None and basis == "calc":
            ratios["leverage"] = round(liabilities / equity, 2)
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
        plain = {k: v["value"] for k, v in values.items()}
        liab, basis = liabilities_for(plain)
        if liab is not None:
            values["liabilities"] = {
                "name": "Обязательства",
                "unit": "млн", "value": liab,
            }
        table = {}
        for code, _label in TABLE_METRIC_CODES:
            table[code] = values.get(code, {}).get("value")

        periods_data.append({
            "year": p.year,
            "values": values,
            "ratios": calculate_ratios_for_period(p),
            "liabilities_basis": basis,
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

    markets = []
    for e in m.market_entries:
        markets.append({
            "id": e.market.id,
            "name": e.market.name,
            "hhi": e.market.hhi,
            "share": round(float(e.share), 2),
            "is_main": bool(e.is_main),
        })
    markets.sort(key=lambda x: (not x["is_main"], -x["share"]))

    return {
        "id": m.id,
        "name": m.name,
        "short_name": m.short_name,
        "inn": m.inn,
        "color": m.color,
        "logo_url": m.logo_url,
        "logo_filename": m.logo_filename,
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
            "market_scope": m.market_scope,
            "flag_emoji": m.country.flag_emoji,
        },
        "currency": currency_of(m),
        "periods": periods_data,
        "growth_rates": calculate_growth_rates(periods),
        "court_cases": court_cases,
        "markets": markets,
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
