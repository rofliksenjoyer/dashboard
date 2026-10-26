from extensions import db
from models import Metric, Industry, Country, MonopolyType


def seed_monopoly_types():
    types = [
        "Естественная монополия",
        "Искусственная монополия",
    ]
    for t in types:
        if not MonopolyType.query.filter_by(name=t).first():
            db.session.add(MonopolyType(name=t))
    db.session.commit()


def seed_metrics():
    metrics = [
        {"code": "revenue",           "name": "Выручка от продаж",                    "unit": "млн"},
        {"code": "net_profit",        "name": "Чистая прибыль (убыток)",              "unit": "млн"},
        {"code": "assets",            "name": "Активы",                               "unit": "млн"},
        {"code": "equity",            "name": "Собственный капитал",                  "unit": "млн"},
        {"code": "credits",           "name": "Кредиты и займы",                      "unit": "млн"},
        {"code": "personnel_costs",   "name": "Затраты на персонал",                  "unit": "млн"},
        {"code": "amortization",      "name": "Амортизация",                          "unit": "млн"},
        {"code": "operating_loss",    "name": "Убыток от операционной деятельности",  "unit": "млн"},
        {"code": "financial_income",  "name": "Финансовые доходы",                    "unit": "млн"},
        {"code": "financial_expenses","name": "Финансовые расходы",                   "unit": "млн"},
    ]
    for m in metrics:
        existing = Metric.query.filter_by(code=m["code"]).first()
        if existing:
            existing.name = m["name"]
            existing.unit = m["unit"]
        else:
            db.session.add(Metric(**m))
    db.session.commit()


def seed_industries():
    industries = [
        {"name": "Железнодорожный транспорт"},
        {"name": "Газовая промышленность"},
        {"name": "Цифровые экосистемы и ИТ"},
        {"name": "Розничная торговля / Ритейл"},
        {"name": "Высокотехнологичные платформы"},
        {"name": "Аэрокосмическая отрасль"},
        {"name": "Автомобилестроение"},
    ]
    for i in industries:
        if not Industry.query.filter_by(name=i["name"]).first():
            db.session.add(Industry(**i))
    db.session.commit()


def seed_countries():
    countries = [
        {"name": "Россия", "code": "RU", "market_scope": "ru",    "flag_emoji": "🇷🇺"},
        {"name": "США",    "code": "US", "market_scope": "world", "flag_emoji": "🇺🇸"},
    ]
    for c in countries:
        existing = Country.query.filter_by(code=c["code"]).first()
        if existing:
            existing.flag_emoji = c["flag_emoji"]
            existing.market_scope = c["market_scope"]
            existing.name = c["name"]
        else:
            db.session.add(Country(**c))
    db.session.commit()


def seed_all():
    seed_monopoly_types()
    seed_metrics()
    seed_industries()
    seed_countries()