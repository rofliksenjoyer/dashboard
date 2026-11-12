from extensions import db
from models import (
    Metric, Industry, Country, MonopolyType, Monopoly, Period, PeriodValue
)


def seed_monopoly_types():
    types = [
        "Естественная монополия",
        "Высокотехнологичная монополия",
        "Платформенная монополия",
        "Капиталоёмкая монополия",
        "Олигополия",
        "Государственная монополия"
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
        {"name": "Автомобилестроение"},
        {"name": "Розничная торговля алкогольной продукцией"},
    ]
    for i in industries:
        if not Industry.query.filter_by(name=i["name"]).first():
            db.session.add(Industry(**i))
    db.session.commit()


def seed_countries():
    countries = [
        {"name": "Россия", "code": "RU", "flag_emoji": "🇷🇺"},
        {"name": "США", "code": "US", "flag_emoji": "🇺🇸"},
        {"name": "Китай", "code": "CN", "flag_emoji": "🇨🇳"},
        {"name": "Япония", "code": "JP", "flag_emoji": "🇯🇵"},
        {"name": "Германия", "code": "DE", "flag_emoji": "🇩🇪"},
        {"name": "Норвегия", "code": "NO", "flag_emoji": "🇳🇴"},
        {"name": "Швеция", "code": "SE", "flag_emoji": "🇸🇪"},
    ]
    for c in countries:
        existing = Country.query.filter_by(code=c["code"]).first()
        if existing:
            existing.flag_emoji = c["flag_emoji"]
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
        market_scope="world",
        industry_id=tech.id,
        monopoly_type_id=mtype.id,
        description="Американская транснациональная корпорация, разработчик и производитель бытовой электроники, программного обеспечения и цифровых сервисов. Штаб-квартира расположена в городе Купертино, штат Калифорния.",
        website="https://apple.com",
        employees=166,
        founded_year=1976,
        logo_url="https://avatars.mds.yandex.net/i?id=7bbf9fda964ea962bd44e247341d8e97ca79a134-4238413-images-thumbs&n=13"
    )
    db.session.add(apple)
    db.session.flush() 

    # Данные по годам
    periods_data = {
        2023: {"revenue": 383285.00, "net_profit": 96995.00, "assets": 352583.00, "equity": 62146.00, "credits": 111088.00},
        2024: {"revenue": 391035.00, "net_profit": 93736.00, "assets": 364980.00, "equity": 56950.00, "credits": 106629.00},
        2025: {"revenue": 416161.00, "net_profit": 112010.00, "assets": 359241.00, "equity": 73733.00, "credits": 98657.00},
    }


    metrics = {m.code: m.id for m in Metric.query.all()}

    for year, data in periods_data.items():
        period = Period(monopoly_id=apple.id, year=year)
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
        inn="91-1144442",
        market_scope="world",  
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
    db.session.flush()  

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
        inn="61-1767919",
        market_scope="world", 
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
    db.session.flush()  

    # Данные по годам (млн долларов)
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

    rzd = Monopoly(
        name='ОАО "Российские железные дороги"',
        short_name="РЖД",
        inn="7708503727",
        market_scope="ru",
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
    db.session.flush()  

 
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
        market_scope="ru",
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
        market_scope="ru",
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
        market_scope="ru",
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
        market_scope="ru",
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
        market_scope="ru",
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
        market_scope="ru",
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

def seed_megafon():
    ru = Country.query.filter_by(code="RU").first()
    telecom = Industry.query.filter_by(name="Телекоммуникации").first()
    mtype = MonopolyType.query.filter_by(name="Олигополия").first()

    if not ru or not telecom or not mtype:
        print("Ошибка: сначала должны быть созданы страна RU, отрасль и тип монополии.")
        return

    if Monopoly.query.filter_by(country_id=ru.id, inn="7812014560").first():
        print("МегаФон уже есть в базе, пропускаем.")
        return

    megafon = Monopoly(
        name='ПАО "МегаФон"',
        short_name="МегаФон",
        inn="7812014560",
        market_scope="ru",
        country_id=ru.id,
        industry_id=telecom.id,
        monopoly_type_id=mtype.id,
        description=(
            "Российская телекоммуникационная компания, предоставляющая услуги "
            "мобильной и фиксированной связи, мобильного и широкополосного "
            "интернета, передачи данных и цифровых сервисов. Компания развивает "
            "собственную телекоммуникационную инфраструктуру, обслуживает "
            "частных и корпоративных клиентов, а также предоставляет решения "
            "в области информационных технологий и цифровых услуг."
        ),
        website="https://www.megafon.ru",
        founded_year=1993,
        logo_url="https://avatars.mds.yandex.net/i?id=b1dac677e6252c9246a0e4f52c5cdab4_l-6311181-images-thumbs&n=13"
    )

    db.session.add(megafon)
    db.session.flush()

    periods_data = {
    2023: {
        "revenue": 444043.00,
        "net_profit": 39982.00,
        "assets": 612058.00,
        "equity": 83556.00,
        "credits": 268449.00
    },
    2024: {
        "revenue": 485923.00,
        "net_profit": 45019.00,
        "assets": 682223.00,
        "equity": 25243.00,
        "credits": 374528.00
    },
    2025: {
        "revenue": 525550.00,
        "net_profit": 41330.00,
        "assets": 715696.00,
        "equity": 19104.00,
        "credits": 396259.00
    },
}

    metrics = {m.code: m.id for m in Metric.query.all()}

    for year, data in periods_data.items():
        period = Period(monopoly_id=megafon.id, year=year)
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
    print("ПАО «МегаФон» успешно добавлено со всеми периодами!")


def seed_vimpelcom():
    ru = Country.query.filter_by(code="RU").first()
    telecom = Industry.query.filter_by(name="Телекоммуникации").first()
    mtype = MonopolyType.query.filter_by(name="Олигополия").first()

    if not ru or not telecom or not mtype:
        print("Ошибка: сначала должны быть созданы страна RU, отрасль и тип монополии.")
        return

    if Monopoly.query.filter_by(country_id=ru.id, inn="7713076301").first():
        print("ВымпелКом уже есть в базе, пропускаем.")
        return

    vimpelcom = Monopoly(
        name='ПАО "ВымпелКом"',
        short_name="Билайн",
        inn="7713076301",
        market_scope="ru",
        country_id=ru.id,
        industry_id=telecom.id,
        monopoly_type_id=mtype.id,
        description=(
            "Российская телекоммуникационная компания, работающая под брендом "
            "билайн. Предоставляет услуги мобильной и фиксированной связи, "
            "мобильного интернета и передачи данных. Компания также развивает "
            "цифровые сервисы, облачные решения, информационную безопасность, "
            "цифровую рекламу и услуги для корпоративных клиентов. "
            "Является одним из крупнейших операторов мобильной связи "
            "на российском рынке."
        ),
        website="https://www.beeline.ru",
        founded_year=1992,
        logo_url="https://stcdn.business-online.ru/articles/cc/1634200407_nD66y0DwuHc.jpg"
    )

    db.session.add(vimpelcom)
    db.session.flush()

    periods_data = {
    2023: {
        "revenue": 303478.00,
        "net_profit": 3372.00,
        "assets": 597408.00,
        "equity": 100687.00,
        "credits": 403255.00
    },
    2024: {
        "revenue": 310716.00,
        "net_profit": 18739.00,
        "assets": 579884.00,
        "equity": 41840.00,
        "credits": 386540.00
    },
    2025: {
        "revenue": 334674.00,
        "net_profit": 23504.00,
        "assets": 541209.00,
        "equity": 54825.00,
        "credits": 403613.00
    }
}
    metrics = {m.code: m.id for m in Metric.query.all()}

    for year, data in periods_data.items():
        period = Period(monopoly_id=vimpelcom.id, year=year)
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
    print("ПАО «ВымпелКом» успешно добавлено со всеми периодами!")

def seed_mts():
    ru = Country.query.filter_by(code="RU").first()
    telecom = Industry.query.filter_by(name="Телекоммуникации").first()
    mtype = MonopolyType.query.filter_by(name="Олигополия").first()

    if not ru or not telecom or not mtype:
        print("Ошибка: сначала должны быть созданы страна RU, отрасль и тип монополии.")
        return

    if Monopoly.query.filter_by(country_id=ru.id, inn="7740000076").first():
        print("МТС уже есть в базе, пропускаем.")
        return

    mts = Monopoly(
        name='ПАО "МТС"',
        short_name="МТС",
        inn="7740000076",
        market_scope="ru",
        country_id=ru.id,
        industry_id=telecom.id,
        monopoly_type_id=mtype.id,
        description=(
            "Российская телекоммуникационная компания, предоставляющая услуги "
            "мобильной и фиксированной связи, широкополосного доступа в интернет, "
            "цифрового телевидения и различных цифровых сервисов. Группа МТС "
            "также развивает направления финансовых технологий, облачных услуг, "
            "медиа и развлечений, информационной безопасности и решений для бизнеса. "
            "Компания является одним из крупнейших операторов мобильной связи "
            "в России."
        ),
        website="https://www.mts.ru",
        founded_year=1993,
        logo_url="https://avatars.mds.yandex.net/i?id=fd239f8b3bc4a95fd1d6c1f48c4134df_l-9097650-images-thumbs&n=13"
    )

    db.session.add(mts)
    db.session.flush()

    periods_data = {
    2023: {
        "revenue": 605991.00,
        "net_profit": 55529.00,
        "assets": 1291545.00,
        "equity": 1720.00,
        "credits": 554055.00
    },
    2024: {
        "revenue": 703741.00,
        "net_profit": 51300.00,
        "assets": 1516963.00,
        "equity": -11234.00,
        "credits": 671779.00
    },
    2025: {
        "revenue": 807186.00,
        "net_profit": 38637.00,
        "assets": 1768424.00,
        "equity": 16958.00,
        "credits": 713057.00
    }
}

    metrics = {m.code: m.id for m in Metric.query.all()}

    for year, data in periods_data.items():
        period = Period(monopoly_id=mts.id, year=year)
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
    print("ПАО «МТС» успешно добавлено со всеми периодами!")

def _seed_chinese_company(
    name,
    short_name,
    uscc,
    industry_name,
    monopoly_type_name,
    description,
    website,
    logo_url,
    founded_year,
    periods_data,
):
    try:
        cn = Country.query.filter_by(code="CN").first()
        industry = Industry.query.filter_by(name=industry_name).first()
        mtype = MonopolyType.query.filter_by(name=monopoly_type_name).first()

        if not cn or not industry or not mtype:
            print(
                f"Ошибка при добавлении {short_name}: "
                "не найдена страна, отрасль или тип монополии."
            )
            return

        # Проверяем USCC в рамках Китая
        existing_company = Monopoly.query.filter_by(
            country_id=cn.id,
            inn=uscc
        ).first()

        if existing_company:
            print(f"{short_name} уже есть в базе, пропускаем.")
            return

        company = Monopoly(
            name=name,
            short_name=short_name,
            inn=uscc,
            market_scope="ru",
            country_id=cn.id,
            industry_id=industry.id,
            monopoly_type_id=mtype.id,
            description=description,
            website=website,
            logo_url=logo_url,
            founded_year=founded_year,
        )

        db.session.add(company)
        db.session.flush()

        metrics = {
            metric.code: metric.id
            for metric in Metric.query.all()
        }

        for year, data in periods_data.items():

            existing_period = Period.query.filter_by(
                monopoly_id=company.id,
                year=year
            ).first()

            if existing_period:
                print(
                    f"Предупреждение: период {year} для "
                    f"{short_name} уже существует."
                )
                continue

            available_data = {
                code: value
                for code, value in data.items()
                if value is not None and code in metrics
            }

            if not available_data:
                continue

            missing_metrics = [
                code for code, value in data.items()
                if value is not None and code not in metrics
            ]

            if missing_metrics:
                print(
                    f"Предупреждение для {short_name}, {year}: "
                    f"не найдены показатели {missing_metrics}"
                )

            period = Period(
                monopoly_id=company.id,
                year=year
            )

            db.session.add(period)
            db.session.flush()

            for code, value in available_data.items():
                db.session.add(
                    PeriodValue(
                        period_id=period.id,
                        metric_id=metrics[code],
                        value=value
                    )
                )

        db.session.commit()
        print(f"{short_name} успешно добавлена.")

    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при добавлении {short_name}: {e}")


def seed_alibaba():

    periods_data = {
        2024: {
            "revenue": 941168,
            "net_profit": 71332,
            "assets": 1764829,
            "equity": 986544,
            "credits": 170776,
        },
        2025: {
            "revenue": 996347,
            "net_profit": 125976,
            "assets": 1804227,
            "equity": 1009858,
            "credits": 230703,
        },
    }

    _seed_chinese_company(
        name="Alibaba Group Holding Limited",
        short_name="Alibaba",
        uscc="91330100799655058B",
        industry_name="Цифровые экосистемы и ИТ",
        monopoly_type_name="Платформенная монополия",
        description=(
            "Крупная китайская технологическая группа, "
            "работающая в сфере электронной коммерции, облачных "
            "вычислений и цифровых платформ."
        ),
        website="https://www.alibabagroup.com",
        founded_year=1999,
        periods_data=periods_data,
        logo_url="https://avatars.mds.yandex.net/i?id=c3c55fe6c703d5e521e9f8e42fe3a0e3_l-5092546-images-thumbs&n=13",
    )

def seed_tencent():


    periods_data = {
        2024: {
            "revenue": 660257,
            "net_profit": 194073,
        },
        2025: {
            "revenue": 751766,
            "net_profit": 224842,
        },
    }

    _seed_chinese_company(
        name="Tencent Holdings Limited",
        short_name="Tencent",
        uscc="9144030071526726XG",
        industry_name="Цифровые экосистемы и ИТ",
        monopoly_type_name="Платформенная монополия",
        description=(
            "Китайская технологическая компания, развивающая "
            "цифровые платформы, социальные сети, мессенджеры, "
            "игровые сервисы и облачные технологии."
        ),
        website="https://www.tencent.com",
        founded_year=1998,
        periods_data=periods_data,
        logo_url="https://avatars.mds.yandex.net/i?id=55af44331ec707aa876b7c3741b68cce_l-4935684-images-thumbs&n=13",
    )

def seed_baidu():


    periods_data = {
        2023: {
            "revenue": 134598,
            "net_profit": 20315,
        },
        2024: {
            "revenue": 133125,
            "net_profit": 23760,
            "assets": 427780,
            "equity": 273742,
        },
        2025: {
            "revenue": 129079,
            "net_profit": 5600,
            "assets": 449157,
            "equity": 266330,
            "credits": 89500,
        },
    }

    _seed_chinese_company(
        name="Baidu, Inc.",
        short_name="Baidu",
        uscc="91110000802100433B",
        industry_name="Цифровые экосистемы и ИТ",
        monopoly_type_name="Высокотехнологичная монополия",
        description=(
            "Китайская технологическая компания, специализирующаяся "
            "на интернет-поиске, искусственном интеллекте, "
            "облачных технологиях и автономном транспорте."
        ),
        website="https://www.baidu.com",
        founded_year=2000,
        periods_data=periods_data,
        logo_url="https://spark.ru/upload/other/b_69beabd2dffb8.jpg",
    )

def seed_china_mobile():


    periods_data = {
        2023: {
            "revenue": 1009309,
            "net_profit": 131766,
        },
        2024: {
            "revenue": 1040759,
            "net_profit": 138373,
            "assets": 2108127,
            "equity": 1396539,
        },
        2025: {
            "revenue": 1050187,
            "net_profit": 137095,
            "assets": 2128182,
            "equity": 1432851,
            "credits": 9748,
        },
    }

    _seed_chinese_company(
        name="China Mobile Communications Group Co., Ltd.",
        short_name="China Mobile",
        uscc="911100007109250324",
        industry_name="Телекоммуникации",
        monopoly_type_name="Олигополия",
        description=(
            "Крупнейший оператор мобильной связи Китая, "
            "предоставляющий услуги мобильной и фиксированной связи, "
            "интернет-доступа и цифровых сервисов."
        ),
        website="https://www.chinamobileltd.com",
        founded_year=2000,
        periods_data=periods_data,
        logo_url="https://avatars.mds.yandex.net/i?id=f5226d42e8e7f718ae6e62e14932fc9b_l-4378045-images-thumbs&n=13",
    )

def seed_china_telecom():


    periods_data = {
        2023: {
            "revenue": 513551,
            "net_profit": 30446,
            "assets": 835814,
            "equity": 447167,
        },
        2024: {
            "revenue": 529417,
            "net_profit": 33012,
            "assets": 866625,
            "equity": 456552,
            "credits": 11532,
        },
        2025: {
            "revenue": 529559,
            "net_profit": 33185,
            "assets": 870644,
            "equity": 468260,
            "credits": 10023,
        },
    }

    _seed_chinese_company(
        name="China Telecommunications Corporation",
        short_name="China Telecom",
        uscc="91110000100017707H",
        industry_name="Телекоммуникации",
        monopoly_type_name="Олигополия",
        description=(
            "Крупная китайская телекоммуникационная компания, "
            "предоставляющая услуги мобильной и фиксированной связи, "
            "широкополосного доступа в интернет и облачных вычислений."
        ),
        website="https://www.chinatelecom-h.com",
        founded_year=2000,
        periods_data=periods_data,
        logo_url="https://avatars.mds.yandex.net/i?id=d20aba92d695319c9d9a8cf35f53bc9f_l-4905400-images-thumbs&n=13",
    )


def seed_china_unicom():


    periods_data = {
        2023: {
            "revenue": 372597,
            "net_profit": 18726,
            "assets": 661051,
            "equity": 353898,
            "credits": 3168,
        },
        2024: {
            "revenue": 389589,
            "net_profit": 20613,
            "assets": 671237,
            "equity": 363570,
            "credits": 3566,
        },
        2025: {
            "revenue": 392223,
            "assets": 669618,
            "equity": 370867,
            "credits": 5483,
        },
    }

    _seed_chinese_company(
        name="China United Network Communications Group Co., Ltd.",
        short_name="China Unicom",
        uscc="91110000MA001HYK9X",
        industry_name="Телекоммуникации",
        monopoly_type_name="Олигополия",
        description=(
            "Крупный китайский оператор телекоммуникационных услуг, "
            "развивающий мобильную и фиксированную связь, "
            "интернет-инфраструктуру и цифровые решения."
        ),
        website="https://www.chinaunicom.com.hk",
        founded_year=2009,
        periods_data=periods_data,
        logo_url="https://avatars.mds.yandex.net/i?id=00a5ba5c6047e465a6e3bf4464ffa32f-5192549-images-thumbs&n=13",
    )


def seed_china_state_railway():


    periods_data = {
        2023: {
            "revenue": 1245394,
            "net_profit": 3304,
            "assets": 9350980,
            "equity": 3222805,
            "credits": 5135791,
        },
        2024: {
            "revenue": 1283038,
            "net_profit": 3881,
            "assets": 9762694,
            "equity": 3562522,
            "credits": 5120677,
        },
        2025: {
            "revenue": 1283038,
            "net_profit": 3881,
            "assets": 9762694,
            "equity": 3562522,
            "credits": 5120677,
        },
    }

    _seed_chinese_company(
        name="China State Railway Group Co., Ltd.",
        short_name="China State Railway",
        uscc="91100000000013477B",
        industry_name="Железнодорожный транспорт",
        monopoly_type_name="Естественная монополия",
        description=(
            "Государственная железнодорожная компания Китая, "
            "осуществляющая управление национальной железнодорожной "
            "сетью и организацию железнодорожных перевозок."
        ),
        website="https://www.china-railway.com.cn",
        founded_year=2013,
        periods_data=periods_data,
        logo_url="https://avatars.mds.yandex.net/i?id=49d659d642fc43b77e780735ad5dbf991f94e202-4766993-images-thumbs&n=13",
    )


def seed_yandex():
    ru = Country.query.filter_by(code="RU").first()
    it = Industry.query.filter_by(name="Цифровые экосистемы и ИТ").first()
    mtype = MonopolyType.query.filter_by(name="Платформенная монополия").first()

    if not ru or not it or not mtype:
        print("Ошибка: сначала должны быть созданы страна RU, отрасль и тип монополии.")
        return

    if Monopoly.query.filter_by(country_id=ru.id, inn="3900019850").first():
        print("Яндекс уже есть в базе, пропускаем.")
        return

    yandex = Monopoly(
        name='МКПАО "ЯНДЕКС"',
        short_name="Яндекс",
        inn="3900019850",
        market_scope="ru",
        country_id=ru.id,
        industry_id=it.id,
        monopoly_type_id=mtype.id,
        description=(
            "Российская технологическая компания, развивающая цифровую "
            "экосистему сервисов. Основные направления деятельности включают "
            "поисковые и рекламные технологии, электронную коммерцию, "
            "транспортные, финансовые, облачные и развлекательные сервисы. "
            "Компания является одним из крупнейших участников российского "
            "рынка цифровых услуг."
        ),
        website="https://yandex.ru",
        founded_year=1997,
        logo_url="https://avatars.mds.yandex.net/i?id=cea44ab2198cdeaea427c09e47507039_l-11951022-images-thumbs&n=13",
    )

    db.session.add(yandex)
    db.session.flush()

    periods_data = {
        2023: {
            "revenue": 798100.00,
            "net_profit": 52100.00,
            "assets": 746400.00,
            "equity": 260600.00,
            "credits": 140800.00
        },
        2024: {
            "revenue": 1094600.00,
            "net_profit": 11500.00,
            "assets": 1098700.00,
            "equity": 293800.00,
            "credits": 368100.00
        },
        2025: {
            "revenue": 1441100.00,
            "net_profit": 79600.00,
            "assets": 1368300.00,
            "equity": 351200.00,
            "credits": 537200.00
        }
    }

    metrics = {
        metric.code: metric.id
        for metric in Metric.query.all()
    }

    for year, data in periods_data.items():
        period = Period(
            monopoly_id=yandex.id,
            year=year
        )

        db.session.add(period)
        db.session.flush()

        for code, value in data.items():
            if code in metrics and value is not None:
                db.session.add(
                    PeriodValue(
                        period_id=period.id,
                        metric_id=metrics[code],
                        value=value
                    )
                )

    db.session.commit()
    print("Яндекс успешно добавлен.")

def seed_vk():
    ru = Country.query.filter_by(code="RU").first()
    it = Industry.query.filter_by(name="Цифровые экосистемы и ИТ").first()
    mtype = MonopolyType.query.filter_by(name="Платформенная монополия").first()

    if not ru or not it or not mtype:
        print("Ошибка: сначала должны быть созданы страна RU, отрасль и тип монополии.")
        return

    if Monopoly.query.filter_by(country_id=ru.id, inn="3900015862").first():
        print("VK уже есть в базе, пропускаем.")
        return

    vk = Monopoly(
        name='МКПАО "ВК"',
        short_name="VK",
        inn="3900015862",
        market_scope="ru",
        country_id=ru.id,
        industry_id=it.id,
        monopoly_type_id=mtype.id,
        description=(
            "Российский технологический холдинг, развивающий цифровые "
            "платформы, социальные сети, коммуникационные и развлекательные "
            "сервисы, видеоплатформы, образовательные и облачные решения. "
            "В экосистему компании входят социальные сети, сервисы "
            "для общения, контентные и технологические продукты."
        ),
        website="https://vk.company.ru",
        founded_year=2006,
        logo_url="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/VK_Compact_Logo_%282021-present%29.svg/500px-VK_Compact_Logo_%282021-present%29.svg.png",
    )

    db.session.add(vk)
    db.session.flush()

    periods_data = {
        2023: {
            "revenue": 132800.00,
            "net_profit": -34291.00,
            "assets": 400700.00,
            "equity": 137534.00,
            "credits": None
        },
        2024: {
            "revenue": 147573.00,
            "net_profit": -94948.00,
            "assets": 333492.00,
            "equity": 44809.00,
            "credits": None
        },
        2025: {
            "revenue": 159960.00,
            "net_profit": -22000.00,
            "assets": 333276.00,
            "equity": 132874.00,
            "credits": None
        }
    }

    metrics = {
        metric.code: metric.id
        for metric in Metric.query.all()
    }

    for year, data in periods_data.items():
        period = Period(
            monopoly_id=vk.id,
            year=year
        )

        db.session.add(period)
        db.session.flush()

        for code, value in data.items():
            if code in metrics and value is not None:
                db.session.add(
                    PeriodValue(
                        period_id=period.id,
                        metric_id=metrics[code],
                        value=value
                    )
                )

    db.session.commit()
    print("VK успешно добавлена.")



def seed_toyota():
    jp = Country.query.filter_by(code="JP").first()
    auto = Industry.query.filter_by(name="Автомобилестроение").first()
    mtype = MonopolyType.query.filter_by(name="Высокотехнологичная монополия").first()

    if not jp or not auto or not mtype:
        print("Ошибка: сначала должны быть созданы страна JP, отрасль и тип монополии.")
        return

    if Monopoly.query.filter_by(country_id=jp.id, inn="9010401023877").first():
        print("Toyota уже есть в базе, пропускаем.")
        return

    toyota = Monopoly(
        name="Toyota Motor Corporation",
        short_name="Toyota",
        inn="9010401023877",
        market_scope="world",
        country_id=jp.id,
        industry_id=auto.id,
        monopoly_type_id=mtype.id,
        description=(
            "Японская автомобильная корпорация, один из крупнейших "
            "мировых производителей автомобилей. Компания выпускает "
            "легковые и коммерческие автомобили, гибридные и "
            "электрические транспортные средства, а также развивает "
            "технологии автономного вождения и мобильности. "
            "В группу Toyota входят бренды Toyota, Lexus, Daihatsu и Hino."
        ),
        website="https://global.toyota",
        founded_year=1937,
        logo_url="https://avatars.mds.yandex.net/i?id=fd6e2665364ae7701d0da3baff8d8c0343a631ca-9211526-images-thumbs&n=13",
    )

    db.session.add(toyota)
    db.session.flush()

    periods_data = {
        2023: {
            "revenue": 264423,
            "net_profit": 17446,
            "assets": 528807,
            "equity": 208270,
            "credits": 209096
        },
        2024: {
            "revenue": 297948,
            "net_profit": 32672,
            "assets": 595392,
            "equity": 232829,
            "credits": 241566
        },
        2025: {
            "revenue": 321032,
            "net_profit": 31845,
            "assets": 625544,
            "equity": 246464,
            "credits": 259255
        }
    }

    metrics = {
        metric.code: metric.id
        for metric in Metric.query.all()
    }

    for year, data in periods_data.items():
        period = Period(
            monopoly_id=toyota.id,
            year=year
        )

        db.session.add(period)
        db.session.flush()

        for code, value in data.items():
            if code in metrics and value is not None:
                db.session.add(
                    PeriodValue(
                        period_id=period.id,
                        metric_id=metrics[code],
                        value=value
                    )
                )

    db.session.commit()
    print("Toyota успешно добавлена.")




def seed_volkswagen():
    de = Country.query.filter_by(code="DE").first()
    auto = Industry.query.filter_by(name="Автомобилестроение").first()
    mtype = MonopolyType.query.filter_by(name="Высокотехнологичная монополия").first()

    if not de or not auto or not mtype:
        print("Ошибка: сначала должны быть созданы страна DE, отрасль и тип монополии.")
        return

    if Monopoly.query.filter_by(country_id=de.id, inn="DE115235681").first():
        print("Volkswagen уже есть в базе, пропускаем.")
        return

    volkswagen = Monopoly(
        name="Volkswagen AG",
        short_name="Volkswagen",
        inn="DE115235681",
        market_scope="world",
        country_id=de.id,
        industry_id=auto.id,
        monopoly_type_id=mtype.id,
        description=(
            "Немецкий автомобильный концерн, один из крупнейших "
            "автопроизводителей мира. Группа занимается разработкой, "
            "производством и продажей легковых и коммерческих автомобилей, "
            "электромобилей и автомобильных технологий. "
            "В состав концерна входят Volkswagen, Audi, Porsche, "
            "Škoda, SEAT, CUPRA, Bentley, Lamborghini и другие бренды."
        ),
        website="https://www.volkswagen-group.com",
        founded_year=1937,
        logo_url="https://avatars.mds.yandex.net/i?id=db505c7c9325d23c1e2da58ad7c2d0e4-5597742-images-thumbs&n=13",
    )

    db.session.add(volkswagen)
    db.session.flush()

    periods_data = {
        2023: {
            "revenue": 348615,
            "net_profit": 19320,
            "assets": 649386,
            "equity": 205428,
            "credits": 251819
        },
        2024: {
            "revenue": 351278,
            "net_profit": 13410,
            "assets": 684803,
            "equity": 212863,
            "credits": 274916
        },
        2025: {
            "revenue": 363955,
            "net_profit": 7806,
            "assets": 728634,
            "equity": 229573,
            "credits": 299273
        }
    }

    metrics = {
        metric.code: metric.id
        for metric in Metric.query.all()
    }

    for year, data in periods_data.items():
        period = Period(
            monopoly_id=volkswagen.id,
            year=year
        )

        db.session.add(period)
        db.session.flush()

        for code, value in data.items():
            if code in metrics and value is not None:
                db.session.add(
                    PeriodValue(
                        period_id=period.id,
                        metric_id=metrics[code],
                        value=value
                    )
                )

    db.session.commit()
    print("Volkswagen успешно добавлена.")




def seed_mercedes():
    de = Country.query.filter_by(code="DE").first()
    auto = Industry.query.filter_by(name="Автомобилестроение").first()
    mtype = MonopolyType.query.filter_by(name="Высокотехнологичная монополия").first()

    if not de or not auto or not mtype:
        print("Ошибка: сначала должны быть созданы страна DE, отрасль и тип монополии.")
        return

    if Monopoly.query.filter_by(country_id=de.id, inn="DE812526315").first():
        print("Mercedes-Benz уже есть в базе, пропускаем.")
        return

    mercedes = Monopoly(
        name="Mercedes-Benz Group AG",
        short_name="Mercedes-Benz",
        inn="DE812526315",
        market_scope="world",
        country_id=de.id,
        industry_id=auto.id,
        monopoly_type_id=mtype.id,
        description=(
            "Немецкая автомобильная компания, специализирующаяся "
            "на производстве легковых автомобилей премиального класса "
            "и коммерческого транспорта. Компания также развивает "
            "электрические автомобили, автомобильное программное "
            "обеспечение, технологии автономного вождения и финансовые "
            "услуги, связанные с приобретением и использованием автомобилей."
        ),
        website="https://group.mercedes-benz.com",
        founded_year=1926,
        logo_url="https://avatars.mds.yandex.net/get-mpic/4519143/2a000001920599d4b2633bc8a12a736d9fa5/orig",
    )

    db.session.add(mercedes)
    db.session.flush()

    periods_data = {
        2023: {
            "revenue": 165736,
            "net_profit": 15718,
            "assets": 281258,
            "equity": 100399,
            "credits": 117514
        },
        2024: {
            "revenue": 157533,
            "net_profit": 11263,
            "assets": 286741,
            "equity": 101308,
            "credits": 119651
        },
        2025: {
            "revenue": 149481,
            "net_profit": 6027,
            "assets": 288830,
            "equity": 106548,
            "credits": 111348
        }
    }

    metrics = {
        metric.code: metric.id
        for metric in Metric.query.all()
    }

    for year, data in periods_data.items():
        period = Period(
            monopoly_id=mercedes.id,
            year=year
        )

        db.session.add(period)
        db.session.flush()

        for code, value in data.items():
            if code in metrics and value is not None:
                db.session.add(
                    PeriodValue(
                        period_id=period.id,
                        metric_id=metrics[code],
                        value=value
                    )
                )

    db.session.commit()
    print("Mercedes-Benz успешно добавлена.")


def seed_vinmonopolet():
    no = Country.query.filter_by(code="NO").first()
    alcohol = Industry.query.filter_by(
        name="Розничная торговля алкогольной продукцией"
    ).first()
    mtype = MonopolyType.query.filter_by(
        name="Государственная монополия"
    ).first()

    if not no or not alcohol or not mtype:
        print("Ошибка: сначала должны быть созданы страна NO, отрасль и тип монополии.")
        return

    if Monopoly.query.filter_by(
        country_id=no.id,
        inn="817209882"
    ).first():
        print("Vinmonopolet уже есть в базе, пропускаем.")
        return

    vinmonopolet = Monopoly(
        name="A/S Vinmonopolet",
        short_name="Vinmonopolet",
        inn="817209882",
        market_scope="ru",
        country_id=no.id,
        industry_id=alcohol.id,
        monopoly_type_id=mtype.id,
        description=(
            "Норвежская государственная компания, обладающая "
            "исключительным правом на розничную продажу большинства "
            "алкогольных напитков крепостью выше 4,7%. Компания "
            "осуществляет продажу крепких алкогольных напитков "
            "через специализированную сеть магазинов. "
            "Основная цель деятельности заключается в обеспечении "
            "ответственной и регулируемой торговли алкогольной продукцией."
        ),
        website="https://www.vinmonopolet.no",
        founded_year=1922,
        logo_url="https://avatars.mds.yandex.net/i?id=431bf61df270125a73f913ba382a1b9b_l-5235970-images-thumbs&n=13",
    )

    db.session.add(vinmonopolet)
    db.session.flush()

    periods_data = {
        2023: {
            "revenue": 18706,
            "net_profit": 304,
            "assets": 4694,
            "equity": 896,
            "credits": 0,
        },
        2024: {
            "revenue": 18646,
            "net_profit": 185,
            "assets": 4272,
            "equity": 1075,
            "credits": 0,
        },
        2025: {
            "revenue": 18681,
            "net_profit": -192,
            "assets": 4662,
            "equity": 862,
            "credits": 0,
        },
    }

    metrics = {
        metric.code: metric.id
        for metric in Metric.query.all()
    }

    for year, data in periods_data.items():
        period = Period(
            monopoly_id=vinmonopolet.id,
            year=year
        )

        db.session.add(period)
        db.session.flush()

        for code, value in data.items():
            if code in metrics and value is not None:
                db.session.add(
                    PeriodValue(
                        period_id=period.id,
                        metric_id=metrics[code],
                        value=value
                    )
                )

    db.session.commit()
    print("Vinmonopolet успешно добавлена.")



def seed_systembolaget():
    se = Country.query.filter_by(code="SE").first()
    alcohol = Industry.query.filter_by(
        name="Розничная торговля алкогольной продукцией"
    ).first()
    mtype = MonopolyType.query.filter_by(
        name="Государственная монополия"
    ).first()

    if not se or not alcohol or not mtype:
        print("Ошибка: сначала должны быть созданы страна SE, отрасль и тип монополии.")
        return

    if Monopoly.query.filter_by(
        country_id=se.id,
        inn="5560599473"
    ).first():
        print("Systembolaget уже есть в базе, пропускаем.")
        return

    systembolaget = Monopoly(
        name="Systembolaget AB",
        short_name="Systembolaget",
        inn="5560599473",
        market_scope="ru",
        country_id=se.id,
        industry_id=alcohol.id,
        monopoly_type_id=mtype.id,
        description=(
            "Шведская государственная компания, обладающая "
            "исключительным правом на розничную продажу большинства "
            "алкогольных напитков. Компания "
            "осуществляет торговлю крепкими алкогольными "
            "напитками через сеть специализированных магазинов. "
            "Деятельность компании направлена на обеспечение "
            "ответственного потребления алкоголя и контроль "
            "за розничной реализацией алкогольной продукции."
        ),
        website="https://www.systembolaget.se",
        founded_year=1955,
        logo_url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Systembolaget_logo_%28new%29.svg/1280px-Systembolaget_logo_%28new%29.svg.png",
    )

    db.session.add(systembolaget)
    db.session.flush()

    # Все значения в млн SEK
    periods_data = {
        2023: {
            "revenue": 38174,
            "net_profit": 409,
            "assets": 7210,
            "equity": 1812,
            "credits": 0,
        },
        2024: {
            "revenue": 39407,
            "net_profit": 362,
            "assets": 7515,
            "equity": 1765,
            "credits": 0,
        },
        2025: {
            "revenue": 39046,
            "net_profit": 57,
            "assets": 6999,
            "equity": 1460,
            "credits": 0,
        },
    }

    metrics = {
        metric.code: metric.id
        for metric in Metric.query.all()
    }

    for year, data in periods_data.items():
        period = Period(
            monopoly_id=systembolaget.id,
            year=year
        )

        db.session.add(period)
        db.session.flush()

        for code, value in data.items():
            if code in metrics and value is not None:
                db.session.add(
                    PeriodValue(
                        period_id=period.id,
                        metric_id=metrics[code],
                        value=value
                    )
                )

    db.session.commit()
    print("Systembolaget успешно добавлена.")


def seed_att():
    us = Country.query.filter_by(code="US").first()
    telecom = Industry.query.filter_by(
        name="Телекоммуникации"
    ).first()
    mtype = MonopolyType.query.filter_by(
        name="Олигополия"
    ).first()

    if not us or not telecom or not mtype:
        print("Ошибка: сначала должны быть созданы страна US, отрасль и тип монополии.")
        return

    if Monopoly.query.filter_by(
        country_id=us.id,
        inn="43-1301883"
    ).first():
        print("AT&T уже есть в базе, пропускаем.")
        return

    att = Monopoly(
        name="AT&T Inc.",
        short_name="AT&T",
        inn="43-1301883",
        market_scope="ru",
        country_id=us.id,
        industry_id=telecom.id,
        monopoly_type_id=mtype.id,
        description=(
            "Американская телекоммуникационная компания, "
            "один из крупнейших операторов связи в США. "
            "Предоставляет услуги мобильной и фиксированной связи, "
            "широкополосного доступа в интернет, а также корпоративные "
            "телекоммуникационные решения. Компания обладает развитой "
            "сетевой инфраструктурой и занимает значительное положение "
            "на американском рынке телекоммуникаций."
        ),
        website="https://www.att.com",
        founded_year=1983,
        hq="Даллас, Техас, США",
        logo_url="https://avatars.mds.yandex.net/i?id=a3b3d1aaba3a828d30471395b8f7b882_l-9182206-images-thumbs&n=13",
    )

    db.session.add(att)
    db.session.flush()

    # Все значения в млн USD
    periods_data = {
        2023: {
            "revenue": 122428,
            "net_profit": 14400,
            "assets": 407060,
            "equity": 117442,
            "credits": 137331,
        },
        2024: {
            "revenue": 122336,
            "net_profit": 10948,
            "assets": 394795,
            "equity": 118245,
            "credits": 123532,
        },
        2025: {
            "revenue": 125648,
            "net_profit": 21953,
            "assets": 420198,
            "equity": 126491,
            "credits": 136100,
        },
    }

    metrics = {
        metric.code: metric.id
        for metric in Metric.query.all()
    }

    for year, data in periods_data.items():
        period = Period(
            monopoly_id=att.id,
            year=year
        )

        db.session.add(period)
        db.session.flush()

        for code, value in data.items():
            if code in metrics and value is not None:
                db.session.add(
                    PeriodValue(
                        period_id=period.id,
                        metric_id=metrics[code],
                        value=value
                    )
                )

    db.session.commit()
    print("AT&T успешно добавлена.")



def seed_verizon():
    us = Country.query.filter_by(code="US").first()
    telecom = Industry.query.filter_by(
        name="Телекоммуникации"
    ).first()
    mtype = MonopolyType.query.filter_by(
        name="Олигополия"
    ).first()

    if not us or not telecom or not mtype:
        print("Ошибка: сначала должны быть созданы страна US, отрасль и тип монополии.")
        return

    if Monopoly.query.filter_by(
        country_id=us.id,
        inn="23-2259884"
    ).first():
        print("Verizon уже есть в базе, пропускаем.")
        return

    verizon = Monopoly(
        name="Verizon Communications Inc.",
        short_name="Verizon",
        inn="23-2259884",
        market_scope="ru",
        country_id=us.id,
        industry_id=telecom.id,
        monopoly_type_id=mtype.id,
        description=(
            "Американская телекоммуникационная компания, "
            "один из ведущих операторов мобильной и фиксированной "
            "связи в США. Предоставляет услуги беспроводной связи, "
            "широкополосного доступа в интернет, а также решения "
            "для корпоративных и государственных клиентов. "
            "Компания развивает инфраструктуру сетей 5G и "
            "оптоволоконной связи и является одним из основных "
            "участников американского телекоммуникационного рынка."
        ),
        website="https://www.verizon.com",
        founded_year=2000,
        hq="Нью-Йорк, США",
        logo_url="https://avatars.mds.yandex.net/get-altay/18780150/2a0000019d8fc547821dcd756d504dd38ddc/orig",
    )

    db.session.add(verizon)
    db.session.flush()

    # Все значения в млн USD
    periods_data = {
        2023: {
            "revenue": 133974,
            "net_profit": 11614,
            "assets": 380255,
            "equity": 93799,
            "credits": 150674,
        },
        2024: {
            "revenue": 134788,
            "net_profit": 17506,
            "assets": 384711,
            "equity": 100575,
            "credits": 144014,
        },
        2025: {
            "revenue": 138191,
            "net_profit": 17174,
            "assets": 404258,
            "equity": 105741,
            "credits": 158150,
        },
    }

    metrics = {
        metric.code: metric.id
        for metric in Metric.query.all()
    }

    for year, data in periods_data.items():
        period = Period(
            monopoly_id=verizon.id,
            year=year
        )

        db.session.add(period)
        db.session.flush()

        for code, value in data.items():
            if code in metrics and value is not None:
                db.session.add(
                    PeriodValue(
                        period_id=period.id,
                        metric_id=metrics[code],
                        value=value
                    )
                )

    db.session.commit()
    print("Verizon успешно добавлена.")


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
    seed_megafon()
    seed_mts()
    seed_vimpelcom()
    seed_alibaba()
    seed_tencent()
    seed_baidu()
    seed_china_mobile()
    seed_china_telecom()
    seed_china_unicom()
    seed_china_state_railway()
    seed_yandex()
    seed_vk()
    seed_toyota()
    seed_volkswagen()
    seed_mercedes()
    seed_vinmonopolet()
    seed_systembolaget()
    seed_att()
    seed_verizon()

    