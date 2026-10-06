from extensions import db
from models import Metric, Industry


def seed_metrics():
    metrics = [
        {"code": "revenue", "name": "Выручка от продаж", "unit": "млн руб."},
        {"code": "net_profit", "name": "Чистая прибыль (убыток)", "unit": "млн руб."},
        {"code": "assets", "name": "Активы", "unit": "млн руб."},
        {"code": "equity", "name": "Собственный капитал", "unit": "млн руб."},
        {"code": "credits", "name": "Кредиты и займы", "unit": "млн руб."},
        {"code": "personnel_costs", "name": "Затраты на персонал", "unit": "млн руб."},
        {"code": "amortization", "name": "Амортизация", "unit": "млн руб."},
        {"code": "operating_loss", "name": "Убыток от операционной деятельности", "unit": "млн руб."},
        {"code": "financial_income", "name": "Финансовые доходы", "unit": "млн руб."},
        {"code": "financial_expenses", "name": "Финансовые расходы", "unit": "млн руб."},
    ]
    for m in metrics:
        if not Metric.query.filter_by(code=m["code"]).first():
            db.session.add(Metric(**m))
    db.session.commit()


def seed_industries():
    industries = [
        {"name": "Топливно-энергетический комплекс", "monopoly_type": "natural"},
        {"name": "Транспорт и логистика", "monopoly_type": "natural"},
        {"name": "Связь и телекоммуникации", "monopoly_type": "natural"},
        {"name": "ЖКХ", "monopoly_type": "natural"},
        {"name": "Металлургия", "monopoly_type": "artificial"},
        {"name": "Нефтегазохимия", "monopoly_type": "artificial"},
    ]
    for i in industries:
        if not Industry.query.filter_by(name=i["name"]).first():
            db.session.add(Industry(**i))
    db.session.commit()