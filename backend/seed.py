from extensions import db
from models import (
    Metric, Industry, Country, MonopolyType, Monopoly, Period, PeriodValue
)


def seed_monopoly_types():
    types = [
        "Естественная монополия",
        "Искусственная монополия",
        "Высокотехнологичная монополия",
        "Платформенная монополия",
        "Олигополия",
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
        {"name": "Нефтегазовая промышленность"},
        {"name": "Цифровые экосистемы и ИТ"},
        {"name": "Розничная торговля / Ритейл"},
        {"name": "Высокотехнологичные платформы"},
        {"name": "Аэрокосмическая отрасль"},
        {"name": "Автомобилестроение"},
        {"name": "Почтовая связь (логистика)"},
        {"name": "Телекоммуникации"},
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


def seed_apple():
    us = Country.query.filter_by(code="US").first()
    tech = Industry.query.filter_by(name="Высокотехнологичные платформы").first()
    mtype = MonopolyType.query.filter_by(name="Высокотехнологичная монополия").first()

    if not us or not tech or not mtype:
        print("Ошибка: сначала должны быть созданы страна US, отрасль и тип монополии.")
        return

    if Monopoly.query.filter_by(country_id=us.id, inn="94-2404110").first():
        print("Apple уже есть в базе, пропускаем.")
        return

    # Создаем компанию
    apple = Monopoly(
        name="Apple Inc.",
        short_name="Apple",
        inn="94-2404110",
        country_id=us.id,
        industry_id=tech.id,
        monopoly_type_id=mtype.id,
        description="Американская транснациональная корпорация, разработчик и производитель бытовой электроники, программного обеспечения и цифровых сервисов. Штаб-квартира расположена в городе Купертино, штат Калифорния.",
        website="https://apple.com",
        employees=166,
        founded_year=1976,
        logo_url="https://avatars.mds.yandex.net/i?id=7bbf9fda964ea962bd44e247341d8e97ca79a134-4238413-images-thumbs&n=13"
    )
    db.session.add(apple)
    db.session.flush() # Чтобы получить apple.id

    # Данные по годам
    periods_data = {
        2023: {"revenue": 383285.00, "net_profit": 96995.00, "assets": 352583.00, "equity": 62146.00, "credits": 111088.00},
        2024: {"revenue": 391035.00, "net_profit": 93736.00, "assets": 364980.00, "equity": 56950.00, "credits": 106629.00},
        2025: {"revenue": 416161.00, "net_profit": 112010.00, "assets": 359241.00, "equity": 73733.00, "credits": 98657.00},
    }

    # Получаем метрики из БД для быстрого доступа
    metrics = {m.code: m.id for m in Metric.query.all()}

    for year, data in periods_data.items():
        period = Period(monopoly_id=apple.id, year=year)
        db.session.add(period)
        db.session.flush() # Получаем period.id

        for code, value in data.items():
            if code in metrics:
                pv = PeriodValue(
                    period_id=period.id,
                    metric_id=metrics[code],
                    value=value
                )
                db.session.add(pv)

    db.session.commit()
    print("Apple Inc. успешно добавлена со всеми периодами!")


def seed_microsoft():
    us = Country.query.filter_by(code="US").first()
    tech = Industry.query.filter_by(name="Высокотехнологичные платформы").first()
    mtype = MonopolyType.query.filter_by(name="Высокотехнологичная монополия").first()

    if not us or not tech or not mtype:
        print("Ошибка: сначала должны быть созданы страна US, отрасль и тип монополии.")
        return

    if Monopoly.query.filter_by(country_id=us.id, inn="91-1144442").first():
        print("Microsoft уже есть в базе, пропускаем.")
        return

    # Создаем компанию
    microsoft = Monopoly(
        name="Microsoft Corporation",
        short_name="Microsoft",
        inn="91-1144442",  # EIN — американский аналог ИНН
        country_id=us.id,
        industry_id=tech.id,
        monopoly_type_id=mtype.id,
        description="Американская транснациональная технологическая корпорация, разработчик программного обеспечения, операционных систем, облачных платформ и цифровых сервисов. Штаб-квартира расположена в городе Редмонд, штат Вашингтон.",
        website="https://www.microsoft.com",
        employees=228,
        founded_year=1975,
        logo_url="https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg"
    )
    db.session.add(microsoft)
    db.session.flush()  # Чтобы получить microsoft.id

    # Данные по годам (млн долларов США)
    periods_data = {
        2023: {
            "revenue": 211915.00,
            "net_profit": 72361.00,
            "assets": 411976.00,
            "equity": 206223.00,
            "credits": 47237.00
        },
        2024: {
            "revenue": 245122.00,
            "net_profit": 88136.00,
            "assets": 512163.00,
            "equity": 268477.00,
            "credits": 51630.00
        },
        2025: {
            "revenue": 281724.00,
            "net_profit": 101832.00,
            "assets": 619003.00,
            "equity": 343479.00,
            "credits": 43151.00
        },
    }

    # Получаем метрики из БД для быстрого доступа
    metrics = {m.code: m.id for m in Metric.query.all()}

    for year, data in periods_data.items():
        period = Period(monopoly_id=microsoft.id, year=year)
        db.session.add(period)
        db.session.flush()

        for code, value in data.items():
            if code in metrics:
                pv = PeriodValue(
                    period_id=period.id,
                    metric_id=metrics[code],
                    value=value
                )
                db.session.add(pv)

    db.session.commit()
    print("Microsoft Corporation успешно добавлена со всеми периодами!")

def seed_google():
    us = Country.query.filter_by(code="US").first()
    tech = Industry.query.filter_by(name="Высокотехнологичные платформы").first()
    mtype = MonopolyType.query.filter_by(name="Платформенная монополия").first()

    if not us or not tech or not mtype:
        print("Ошибка: сначала должны быть созданы страна US, отрасль и тип монополии.")
        return

    if Monopoly.query.filter_by(country_id=us.id, inn="61-1767919").first():
        print("Google уже есть в базе, пропускаем.")
        return

    # Создаем компанию
    google = Monopoly(
        name="Alphabet Inc.",
        short_name="Google",
        inn="61-1767919",  # EIN — американский аналог ИНН
        country_id=us.id,
        industry_id=tech.id,
        monopoly_type_id=mtype.id,
        description="Американская транснациональная технологическая корпорация, материнская компания Google. Основные направления деятельности включают поисковую систему Google, цифровую рекламу, видеохостинг YouTube, облачные сервисы Google Cloud и операционную систему Android. Штаб-квартира расположена в городе Маунтин-Вью, штат Калифорния.",
        website="https://www.google.com",
        employees=190.82,
        founded_year=1998,
        logo_url="https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg"
    )
    db.session.add(google)
    db.session.flush()  # Чтобы получить google.id

    # Данные по годам (млн долларов США)
    periods_data = {
        2023: {
            "revenue": 307394.00,
            "net_profit": 73795.00,
            "assets": 402392.00,
            "equity": 283379.00,
            "credits": 27121.00
        },
        2024: {
            "revenue": 350018.00,
            "net_profit": 100118.00,
            "assets": 450256.00,
            "equity": 325084.00,
            "credits": 22574.00
        },
        2025: {
            "revenue": 402836.00,
            "net_profit": 132170.00,
            "assets": 595281.00,
            "equity": 415265.00,
            "credits": 59291.00
        },
    }

    # Получаем метрики из БД для быстрого доступа
    metrics = {m.code: m.id for m in Metric.query.all()}

    for year, data in periods_data.items():
        period = Period(monopoly_id=google.id, year=year)
        db.session.add(period)
        db.session.flush()

        for code, value in data.items():
            if code in metrics:
                pv = PeriodValue(
                    period_id=period.id,
                    metric_id=metrics[code],
                    value=value
                )
                db.session.add(pv)

    db.session.commit()
    print("Alphabet Inc. (Google) успешно добавлена со всеми периодами!")


def seed_rzd():
    ru = Country.query.filter_by(code="RU").first()
    railway = Industry.query.filter_by(name="Железнодорожный транспорт").first()
    mtype = MonopolyType.query.filter_by(name="Естественная монополия").first()

    if not ru or not railway or not mtype:
        print("Ошибка: сначала должны быть созданы страна RU, отрасль и тип монополии.")
        return

    if Monopoly.query.filter_by(country_id=ru.id, inn="7708503727").first():
        print("РЖД уже есть в базе, пропускаем.")
        return

    # Создаем компанию
    rzd = Monopoly(
        name='ОАО "Российские железные дороги"',
        short_name="РЖД",
        inn="7708503727",
        country_id=ru.id,
        industry_id=railway.id,
        monopoly_type_id=mtype.id,
        description="Российская государственная железнодорожная компания, осуществляющая грузовые и пассажирские перевозки, а также управление железнодорожной инфраструктурой общего пользования. Компания обеспечивает функционирование основной части железнодорожной сети России. Единственным акционером является Российская Федерация. Штаб-квартира расположена в Москве.",
        website="https://company.rzd.ru",
        employees=711,
        founded_year=2003,
        logo_url="https://avatars.mds.yandex.net/i?id=fb7a6ebde5e428ce242f8a433995a7cc19b1a0be-13079322-images-thumbs&n=13"
    )
    db.session.add(rzd)
    db.session.flush()  # Чтобы получить rzd.id

    # Данные по годам (млн рублей, консолидированная отчетность МСФО)
    periods_data = {
        2023: {
            "revenue": 3017506.00,
            "net_profit": 170086.00,
            "assets": 8200358.00,
            "equity": 4587764.00,
            "credits": 1983000.00
        },
        2024: {
            "revenue": 3296301.00,
            "net_profit": 50695.00,
            "assets": 9660835.00,
            "equity": 4644889.00,
            "credits": 2989881.00
        },
        2025: {
            "revenue": 3637906.00,
            "net_profit": 2309.00,
            "assets": 10476853.00,
            "equity": 4634272.00,
            "credits": 3783251.00
        },
    }

    # Получаем метрики из БД для быстрого доступа
    metrics = {m.code: m.id for m in Metric.query.all()}

    for year, data in periods_data.items():
        period = Period(monopoly_id=rzd.id, year=year)
        db.session.add(period)
        db.session.flush()

        for code, value in data.items():
            if code in metrics:
                pv = PeriodValue(
                    period_id=period.id,
                    metric_id=metrics[code],
                    value=value
                )
                db.session.add(pv)

    db.session.commit()
    print("ОАО «Российские железные дороги» успешно добавлено со всеми периодами!")


def seed_gazprom():
    ru = Country.query.filter_by(code="RU").first()
    oil_gas = Industry.query.filter_by(name="Нефтегазовая промышленность").first()
    mtype = MonopolyType.query.filter_by(name="Естественная монополия").first()

    if not ru or not oil_gas or not mtype:
        print("Ошибка: сначала должны быть созданы страна RU, отрасль и тип монополии.")
        return

    if Monopoly.query.filter_by(country_id=ru.id, inn="7736050003").first():
        print("Газпром уже есть в базе, пропускаем.")
        return

    gazprom = Monopoly(
        name='ПАО "Газпром"',
        short_name="Газпром",
        inn="7736050003",
        country_id=ru.id,
        industry_id=oil_gas.id,
        monopoly_type_id=mtype.id,
        description=(
            "Крупная российская энергетическая компания, осуществляющая "
            "геологоразведку, добычу, транспортировку, хранение, переработку "
            "и реализацию природного газа, нефти и продуктов их переработки. "
            "Группа Газпром также занимается производством и сбытом тепловой "
            "и электрической энергии. ПАО «Газпром» является головной компанией "
            "группы и владеет крупнейшей в мире системой транспортировки газа."
        ),
        website="https://www.gazprom.ru",
        employees=500.4,
        founded_year=1989,
        logo_url="https://avatars.mds.yandex.net/i?id=dc9d5a417f97d0e4cf6ed061e93d5459_l-8365662-images-thumbs&n=13"
    )

    db.session.add(gazprom)
    db.session.flush()

    periods_data = {
        2023: {
            "revenue": 8541818.00,
            "net_profit": 726000.00,
            "assets": 28713748.00,
            "equity": 16452714.00,
            "credits": 6657000.00
        },
        2024: {
            "revenue": 10714686.00,
            "net_profit": 1461000.00,
            "assets": 30698255.00,
            "equity": 17660962.00,
            "credits": 6715000.00
        },
        2025: {
            "revenue": 9770671.00,
            "net_profit": 1074000.00,
            "assets": 31890811.00,
            "equity": 18893689.00,
            "credits": 6738000.00
        },
    }

    metrics = {m.code: m.id for m in Metric.query.all()}

    for year, data in periods_data.items():
        period = Period(monopoly_id=gazprom.id, year=year)
        db.session.add(period)
        db.session.flush()

        for code, value in data.items():
            if code in metrics:
                pv = PeriodValue(
                    period_id=period.id,
                    metric_id=metrics[code],
                    value=value
                )
                db.session.add(pv)

    db.session.commit()
    print("ПАО «Газпром» успешно добавлено со всеми периодами!")


def seed_transneft():
    ru = Country.query.filter_by(code="RU").first()
    oil_gas = Industry.query.filter_by(name="Нефтегазовая промышленность").first()
    mtype = MonopolyType.query.filter_by(name="Естественная монополия").first()

    if not ru or not oil_gas or not mtype:
        print("Ошибка: сначала должны быть созданы страна RU, отрасль и тип монополии.")
        return

    if Monopoly.query.filter_by(country_id=ru.id, inn="7706061801").first():
        print("Транснефть уже есть в базе, пропускаем.")
        return

    transneft = Monopoly(
        name='ПАО «Транснефть»',
        short_name="Транснефть",
        inn="7706061801",
        country_id=ru.id,
        industry_id=oil_gas.id,
        monopoly_type_id=mtype.id,
        description=(
            "Российская компания, осуществляющая транспортировку нефти "
            "и нефтепродуктов по магистральным трубопроводам. ПАО «Транснефть» "
            "управляет крупнейшей в мире системой магистральных нефтепроводов, "
            "обеспечивает транспортировку нефти от мест добычи до нефтеперерабатывающих "
            "заводов, морских портов и экспортных направлений. Компания также "
            "занимается эксплуатацией и развитием трубопроводной инфраструктуры."
        ),
        website="https://www.transneft.ru",
        founded_year=1993,
        logo_url="https://avatars.mds.yandex.net/i?id=c9e629c8b37f358bdd5dc547ed867c938bca72d2-4864596-images-thumbs&n=13"
    )

    db.session.add(transneft)
    db.session.flush()

    periods_data = {
        2023: {
            "revenue": 1330899.00,
            "net_profit": 314282.00,
            "assets": 3542024.00,
            "equity": 2750433.00,
            "credits": 346229.00
        },
        2024: {
            "revenue": 1423904.00,
            "net_profit": 299976.00,
            "assets": 3691024.00,
            "equity": 2927953.00,
            "credits": 275934.00
        },
        2025: {
            "revenue": 1440281.00,
            "net_profit": 241127.00,
            "assets": 3702383.00,
            "equity": 3003155.00,
            "credits": 206993.00
        },
    }

    metrics = {m.code: m.id for m in Metric.query.all()}

    for year, data in periods_data.items():
        period = Period(monopoly_id=transneft.id, year=year)
        db.session.add(period)
        db.session.flush()

        for code, value in data.items():
            if code in metrics:
                pv = PeriodValue(
                    period_id=period.id,
                    metric_id=metrics[code],
                    value=value
                )
                db.session.add(pv)

    db.session.commit()
    print("ПАО «Транснефть» успешно добавлено со всеми периодами!")


def seed_rosneft():
    ru = Country.query.filter_by(code="RU").first()
    oil_gas = Industry.query.filter_by(name="Нефтегазовая промышленность").first()
    mtype = MonopolyType.query.filter_by(name="Олигополия").first()

    if not ru or not oil_gas or not mtype:
        print("Ошибка: сначала должны быть созданы страна RU, отрасль и тип монополии.")
        return

    if Monopoly.query.filter_by(country_id=ru.id, inn="7706107510").first():
        print("Роснефть уже есть в базе, пропускаем.")
        return

    rosneft = Monopoly(
        name='ПАО "НК "Роснефть"',
        short_name="Роснефть",
        inn="7706107510",
        country_id=ru.id,
        industry_id=oil_gas.id,
        monopoly_type_id=mtype.id,
        description=(
            "Российская вертикально интегрированная нефтяная компания, "
            "осуществляющая разведку и добычу нефти и газа, переработку "
            "углеводородов, производство нефтепродуктов и их реализацию. "
            "Компания объединяет предприятия добывающего, перерабатывающего "
            "и сбытового направлений и является одним из крупнейших "
            "участников российского нефтегазового рынка."
        ),
        website="https://www.rosneft.ru",
        founded_year=1993,
        logo_url="https://avatars.mds.yandex.net/i?id=72c0b8018089d99a7ec99f9be3d433b1832ad44a-10507506-images-thumbs&n=13"
    )

    db.session.add(rosneft)
    db.session.flush()

    periods_data = {
        2023: {
            "revenue": 9163000.00,
            "net_profit": 1529000.00,
            "assets": 18787000.00,
            "equity": 8414000.00,
            "credits": 2700000.00
        },
        2024: {
            "revenue": 10139000.00,
            "net_profit": 1341000.00,
            "assets": 20682000.00,
            "equity": 9157000.00,
            "credits": 3635000.00
        },
        2025: {
            "revenue": 8236000.00,
            "net_profit": 544000.00,
            "assets": 21560000.00,
            "equity": 9078000.00
        },
    }

    metrics = {m.code: m.id for m in Metric.query.all()}

    for year, data in periods_data.items():
        period = Period(monopoly_id=rosneft.id, year=year)
        db.session.add(period)
        db.session.flush()

        for code, value in data.items():
            if code in metrics:
                pv = PeriodValue(
                    period_id=period.id,
                    metric_id=metrics[code],
                    value=value
                )
                db.session.add(pv)

    db.session.commit()
    print("ПАО «НК «Роснефть» успешно добавлено со всеми периодами!")

def seed_lukoil():
    ru = Country.query.filter_by(code="RU").first()
    oil_gas = Industry.query.filter_by(name="Нефтегазовая промышленность").first()
    mtype = MonopolyType.query.filter_by(name="Олигополия").first()

    if not ru or not oil_gas or not mtype:
        print("Ошибка: сначала должны быть созданы страна RU, отрасль и тип монополии.")
        return

    if Monopoly.query.filter_by(country_id=ru.id, inn="7708004767").first():
        print("ЛУКОЙЛ уже есть в базе, пропускаем.")
        return

    lukoil = Monopoly(
        name='ПАО "ЛУКОЙЛ"',
        short_name="ЛУКОЙЛ",
        inn="7708004767",
        country_id=ru.id,
        industry_id=oil_gas.id,
        monopoly_type_id=mtype.id,
        description=(
            "Российская вертикально интегрированная нефтяная компания, "
            "осуществляющая разведку и добычу нефти и газа, переработку "
            "углеводородного сырья, производство нефтепродуктов и их сбыт. "
            "Компания также занимается транспортировкой и реализацией "
            "нефти и нефтепродуктов, управляет сетью автозаправочных станций "
            "и предприятиями нефтепереработки."
        ),
        website="https://www.lukoil.ru",
        founded_year=1991,
        logo_url="https://sbgaz.ru/upload/iblock/fc5/j4v7oibld69df234w7ciptzwpp8hheo0/82.jpg"
    )

    db.session.add(lukoil)
    db.session.flush()

    periods_data = {
        2023: {
            "revenue": 7928303.00,
            "net_profit": 1160271.00,
            "assets": 8600173.00,
            "equity": 6401233.00,
            "credits": 192177.00
        },
        2024: {
            "revenue": 4420565.00,
            "net_profit": 851546.00,
            "assets": 9282619.00,
            "equity": 6892008.00,
            "credits": 380006.00
        },
        2025: {
            "revenue": 3767768.00,
            "net_profit": -1059859.00,
            "assets": 5474421.00,
            "equity": 3626453.00,
            "credits": 318012.00
        },
    }

    metrics = {m.code: m.id for m in Metric.query.all()}

    for year, data in periods_data.items():
        period = Period(monopoly_id=lukoil.id, year=year)
        db.session.add(period)
        db.session.flush()

        for code, value in data.items():
            if code in metrics:
                pv = PeriodValue(
                    period_id=period.id,
                    metric_id=metrics[code],
                    value=value
                )
                db.session.add(pv)

    db.session.commit()
    print("ПАО «ЛУКОЙЛ» успешно добавлено со всеми периодами!")


def seed_pochta_rossii():
    ru = Country.query.filter_by(code="RU").first()
    postal = Industry.query.filter_by(name="Почтовая связь (логистика)").first()
    mtype = MonopolyType.query.filter_by(name="Естественная монополия").first()

    if not ru or not postal or not mtype:
        print("Ошибка: сначала должны быть созданы страна RU, отрасль и тип монополии.")
        return

    if Monopoly.query.filter_by(country_id=ru.id, inn="7724490000").first():
        print("Почта России уже есть в базе, пропускаем.")
        return

    pochta = Monopoly(
        name='АО "Почта России"',
        short_name="Почта России",
        inn="7724490000",
        country_id=ru.id,
        industry_id=postal.id,
        monopoly_type_id=mtype.id,
        description=(
            "Российский национальный оператор почтовой связи, осуществляющий "
            "прием, обработку, перевозку и доставку почтовых отправлений. "
            "Компания предоставляет услуги почтовой связи, занимается "
            "доставкой посылок, выплатой пенсий и пособий, денежными переводами, "
            "логистикой и обслуживанием электронной коммерции. Почта России "
            "обеспечивает предоставление универсальных услуг почтовой связи "
            "на территории страны, включая отдаленные и труднодоступные регионы. "
            "Единственным акционером компании является Российская Федерация."
        ),
        website="https://www.pochta.ru",
        employees=211.6,
        founded_year=2019,
        logo_url="https://atr42.ru/foto3/fotonew9/NWPS3032011.jpg"
    )

    db.session.add(pochta)
    db.session.flush()

    periods_data = {
        2023: {
            "revenue": 222066.00,
            "net_profit": -8081.00,
            "assets": 456009.00,
            "equity": 56826.00,
            "credits": 106790.00
        },
        2024: {
            "revenue": 225597.00,
            "net_profit": -17124.00,
            "assets": 473384.00,
            "equity": 64211.00,
            "credits": 126145.00
        },
        2025: {
            "revenue": 218406.00,
            "net_profit": -23448.00,
            "assets": 442166.00,
            "equity": 54575.00,
            "credits": 126595.00
        },
    }

    metrics = {m.code: m.id for m in Metric.query.all()}

    for year, data in periods_data.items():
        period = Period(monopoly_id=pochta.id, year=year)
        db.session.add(period)
        db.session.flush()

        for code, value in data.items():
            if code in metrics:
                pv = PeriodValue(
                    period_id=period.id,
                    metric_id=metrics[code],
                    value=value
                )
                db.session.add(pv)

    db.session.commit()
    print("АО «Почта России» успешно добавлено со всеми периодами!")


def seed_rostelecom():
    ru = Country.query.filter_by(code="RU").first()
    telecom = Industry.query.filter_by(name="Телекоммуникации").first()
    mtype = MonopolyType.query.filter_by(name="Естественная монополия").first()

    if not ru or not telecom or not mtype:
        print("Ошибка: сначала должны быть созданы страна RU, отрасль и тип монополии.")
        return

    if Monopoly.query.filter_by(country_id=ru.id, inn="7707049388").first():
        print("Ростелеком уже есть в базе, пропускаем.")
        return

    rostelecom = Monopoly(
        name='ПАО "Ростелеком"',
        short_name="Ростелеком",
        inn="7707049388",
        country_id=ru.id,
        industry_id=telecom.id,
        monopoly_type_id=mtype.id,
        description=(
            "Российская телекоммуникационная компания, предоставляющая услуги "
            "фиксированной и мобильной связи, широкополосного доступа в интернет, "
            "цифрового телевидения и облачных сервисов. Компания развивает и "
            "эксплуатирует масштабную волоконно-оптическую инфраструктуру, "
            "обеспечивает передачу данных и предоставляет цифровые решения "
            "для частных клиентов, бизнеса и государственных организаций. "
            "Также Ростелеком участвует в реализации проектов по развитию "
            "цифровой инфраструктуры и информационной безопасности."
        ),
        website="https://www.company.rt.ru",
        founded_year=1993,
        logo_url="https://www.company.rt.ru/about/identity/files/RGB_RT_logo-horizontal_main_ru.png"
    )

    db.session.add(rostelecom)
    db.session.flush()

    periods_data = {
        2023: {
            "revenue": 707801.00,
            "net_profit": 42327.00,
            "assets": 1244077.00,
            "equity": 274557.00,
            "credits": 487871.00
        },
        2024: {
            "revenue": 779945.00,
            "net_profit": 24060.00,
            "assets": 1380952.00,
            "equity": 273609.00,
            "credits": 571819.00
        },
        2025: {
            "revenue": 872790.00,
            "net_profit": 18715.00,
            "assets": 1432881.00,
            "equity": 280199.00,
            "credits": 572243.00
        },
    }

    metrics = {m.code: m.id for m in Metric.query.all()}

    for year, data in periods_data.items():
        period = Period(monopoly_id=rostelecom.id, year=year)
        db.session.add(period)
        db.session.flush()

        for code, value in data.items():
            if code in metrics:
                pv = PeriodValue(
                    period_id=period.id,
                    metric_id=metrics[code],
                    value=value
                )
                db.session.add(pv)

    db.session.commit()
    print("ПАО «Ростелеком» успешно добавлено со всеми периодами!")

def seed_all():
    seed_monopoly_types()
    seed_metrics()
    seed_industries()
    seed_countries()
    seed_apple()
    seed_microsoft()
    seed_google()
    seed_rzd()
    seed_gazprom()
    seed_transneft()
    seed_rosneft()
    seed_lukoil()
    seed_pochta_rossii()
    seed_rostelecom()

    