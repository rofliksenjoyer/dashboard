from extensions import db
from models import Metric, Industry, Country, Monopoly, Period, PeriodValue


def seed_metrics():
    metrics = [
        {"code": "revenue",         "name": "Выручка от продаж",   "unit": "млн"},
        {"code": "net_profit",      "name": "Чистая прибыль",      "unit": "млн"},
        {"code": "assets",          "name": "Активы",              "unit": "млн"},
        {"code": "equity",          "name": "Собственный капитал", "unit": "млн"},
        {"code": "credits",         "name": "Кредиты и займы",     "unit": "млн"},
        {"code": "personnel_costs", "name": "Затраты на персонал", "unit": "млн"},
        {"code": "amortization",    "name": "Амортизация",         "unit": "млн"},
    ]
    for m in metrics:
        if not Metric.query.filter_by(code=m["code"]).first():
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
        {"name": "Россия", "code": "RU", "market_scope": "ru"},
        {"name": "США",    "code": "US", "market_scope": "world"},
    ]
    for c in countries:
        if not Country.query.filter_by(code=c["code"]).first():
            db.session.add(Country(**c))
    db.session.commit()


def _ind(name):
    return Industry.query.filter_by(name=name).first()


def _cty(code):
    return Country.query.filter_by(code=code).first()


def seed_monopolies():
    ru = _cty("RU")
    us = _cty("US")

    data = [
        ("ОАО «РЖД»", "РЖД", "7708031614", "#dc2626", ru,
         "Железнодорожный транспорт", "natural", "natural",
         "Железнодорожные грузовые и пассажирские перевозки, управление инфраструктурой путей сообщения РФ",
         720, 2_900_000, 2003, "Москва, Россия"),

        ("ПАО «Газпром»", "Газпром", "7736050003", "#2563eb", ru,
         "Газовая промышленность", "natural", "resource",
         "Добыча, транспортировка, хранение и реализация природного газа; нефтепереработка и электроэнергетика",
         480, 8_600_000, 1989, "Санкт-Петербург, Россия"),

        ("ПАО «Новатэк»", "Новатэк", "8904035888", "#0891b2", ru,
         "Газовая промышленность", "artificial", "resource",
         "Добыча и реализация природного газа и жидких углеводородов; производство СПГ",
         12, 1_400_000, 1994, "Тарко-Сале, Россия"),

        ("ООО «Яндекс»", "Яндекс", "7736207543", "#dc2626", ru,
         "Цифровые экосистемы и ИТ", "artificial", "platform",
         "Поисковые системы, цифровые сервисы, такси, доставка еды, облачные технологии, ИИ-решения",
         21, 900_000, 1997, "Москва, Россия"),

        ("VK (ВКонтакте)", "VK", "7811030136", "#2563eb", ru,
         "Цифровые экосистемы и ИТ", "artificial", "platform",
         "Социальные сети, мессенджеры, игровые платформы, облачные сервисы, образовательные технологии",
         10, 130_000, 2006, "Москва, Россия"),

        ("X5 Group", "X5", "7729543454", "#16a34a", ru,
         "Розничная торговля / Ритейл", "artificial", "platform",
         "Управление сетями супермаркетов «Пятёрочка», «Перекрёсток», «Чижик»; онлайн-ритейл",
         380, 3_600_000, 2006, "Москва, Россия"),

        ("ПАО «Магнит»", "Магнит", "2309085637", "#dc2626", ru,
         "Розничная торговля / Ритейл", "artificial", "platform",
         "Розничная торговля продуктами питания и товарами повседневного спроса; аптечная сеть",
         340, 2_900_000, 1994, "Краснодар, Россия"),

        ("Alphabet (Google)", "Google", "000000000001", "#4285f4", us,
         "Высокотехнологичные платформы", "artificial", "platform",
         "Поисковые системы, цифровая реклама, облачные вычисления, ИИ, YouTube, Android, автономные автомобили",
         182, 307_000, 1998, "Маунтин-Вью, США"),

        ("Apple Inc.", "Apple", "000000000002", "#1d1d1f", us,
         "Высокотехнологичные платформы", "artificial", "hightech",
         "Производство смартфонов, компьютеров, носимых устройств; экосистема iOS/macOS; стриминг и сервисы",
         164, 383_000, 1976, "Купертино, США"),

        ("Microsoft Corp.", "Microsoft", "000000000003", "#0078d4", us,
         "Высокотехнологичные платформы", "artificial", "platform",
         "Операционные системы, облачные сервисы Azure, офисный пакет Microsoft 365, ИИ-решения, игровые платформы",
         221, 245_000, 1975, "Редмонд, США"),

        ("Boeing Company", "Boeing", "000000000004", "#1d4ed8", us,
         "Аэрокосмическая отрасль", "artificial", "hightech",
         "Производство коммерческих самолётов, военной авиации, космических систем и оборонных технологий",
         172, 78_000, 1916, "Арлингтон, США"),

        ("Airbus SE", "Airbus", "000000000005", "#00205b", us,
         "Аэрокосмическая отрасль", "artificial", "hightech",
         "Производство гражданских и военных самолётов, вертолётов, космических систем и оборонных решений",
         134, 65_000, 1970, "Лейден, Нидерланды"),

        ("Toyota Motor Corp.", "Toyota", "000000000006", "#eb0a1e", us,
         "Автомобилестроение", "artificial", "hightech",
         "Производство легковых и коммерческих автомобилей, гибридных и водородных технологий, финансовые услуги",
         375, 274_000, 1937, "Тоёта, Япония"),

        ("Volkswagen AG", "VW", "000000000007", "#001e50", us,
         "Автомобилестроение", "artificial", "hightech",
         "Производство автомобилей под брендами VW, Audi, Porsche, Skoda, SEAT; электромобили и цифровые сервисы",
         684, 293_000, 1937, "Вольфсбург, Германия"),

        ("Tesla Inc.", "Tesla", "000000000008", "#cc0000", us,
         "Автомобилестроение", "artificial", "hightech",
         "Производство электромобилей, аккумуляторных систем, солнечной энергетики и программного обеспечения",
         140, 97_000, 2003, "Остин, США"),
    ]

    for (name, short, inn, color, country, ind_name, mtype, badge,
         activity, employees, revenue, founded, hq) in data:
        industry = _ind(ind_name)
        if not industry or not country:
            continue
        if Monopoly.query.filter_by(country_id=country.id, inn=inn).first():
            continue
        m = Monopoly(
            name=name, short_name=short, inn=inn, color=color,
            country=country, industry=industry,
            monopoly_type=mtype, badge_type=badge,
            activity=activity, employees=employees,
            founded_year=founded, hq=hq,
        )
        db.session.add(m)
        db.session.flush()

        p = Period(monopoly_id=m.id, year=2024)
        db.session.add(p)
        db.session.flush()

        rev_metric = Metric.query.filter_by(code="revenue").first()
        profit_metric = Metric.query.filter_by(code="net_profit").first()
        if rev_metric:
            db.session.add(PeriodValue(period_id=p.id, metric_id=rev_metric.id, value=revenue))
        if profit_metric:
            db.session.add(PeriodValue(period_id=p.id, metric_id=profit_metric.id, value=int(revenue * 0.10)))

    db.session.commit()


def seed_all():
    seed_metrics()
    seed_industries()
    seed_countries()
    seed_monopolies()