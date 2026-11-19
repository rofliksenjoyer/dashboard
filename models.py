from extensions import db


class Country(db.Model):
    __tablename__ = "countries"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(3), nullable=False, unique=True)
    flag_emoji = db.Column(db.String(8), nullable=True)
    currency = db.Column(db.String(3), nullable=True)

    monopolies = db.relationship("Monopoly", back_populates="country", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Country {self.code}>"

class Industry(db.Model):
    __tablename__ = "industries"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    monopolies = db.relationship("Monopoly", back_populates="industry", lazy=True, cascade="all, delete-orphan")
    markets = db.relationship("Market", back_populates="industry", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Industry {self.name}>"

    def __str__(self):
        return self.name

class MonopolyType(db.Model):
    __tablename__ = "monopoly_types"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f"<MonopolyType {self.name}>"

    def __str__(self):
        return self.name

class Monopoly(db.Model):
    __tablename__ = "monopolies"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    short_name = db.Column(db.String(100), nullable=True)
    inn = db.Column(db.String(18), nullable=False)
    color = db.Column(db.String(20), nullable=True)
    logo_url = db.Column(db.String(500), nullable=True)
    logo_filename = db.Column(db.String(255), nullable=True)

    market_scope = db.Column(db.String(10), nullable=False, default="ru")

    country_id = db.Column(db.Integer, db.ForeignKey("countries.id"), nullable=False)
    industry_id = db.Column(db.Integer, db.ForeignKey("industries.id"), nullable=False)

    description = db.Column(db.Text, nullable=True)
    activity = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(200), nullable=True)
    employees = db.Column(db.Integer, nullable=True)
    founded_year = db.Column(db.Integer, nullable=True)
    hq = db.Column(db.String(200), nullable=True)

    country = db.relationship("Country", back_populates="monopolies")
    industry = db.relationship("Industry", back_populates="monopolies")
    periods = db.relationship("Period", back_populates="monopoly", lazy=True, cascade="all, delete-orphan")
    court_cases = db.relationship("CourtCase", back_populates="monopoly", lazy=True, cascade="all, delete-orphan")
    market_entries = db.relationship("MonopolyMarket", back_populates="monopoly", lazy=True, cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint("country_id", "inn"),
        db.Index("ix_monopoly_country_industry", "country_id", "industry_id"),
    )

    def __repr__(self):
        return f"<Monopoly {self.name}>"


class Period(db.Model):
    __tablename__ = "periods"
    id = db.Column(db.Integer, primary_key=True)
    monopoly_id = db.Column(
        db.Integer, db.ForeignKey("monopolies.id"), nullable=False
    )
    year = db.Column(db.Integer, nullable=False)

    monopoly = db.relationship("Monopoly", back_populates="periods")
    values = db.relationship(
        "PeriodValue", back_populates="period",
        lazy=True, cascade="all, delete-orphan",
    )

    __table_args__ = (
        db.UniqueConstraint("monopoly_id", "year"),
        db.Index("ix_period_year", "year"),
    )


class Metric(db.Model):
    __tablename__ = "metrics"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    unit = db.Column(db.String(20), nullable=True)

    values = db.relationship("PeriodValue", back_populates="metric")

    def __str__(self):
        return self.name


class PeriodValue(db.Model):
    __tablename__ = "period_values"
    id = db.Column(db.Integer, primary_key=True)
    period_id = db.Column(
        db.Integer, db.ForeignKey("periods.id"), nullable=False
    )
    metric_id = db.Column(
        db.Integer, db.ForeignKey("metrics.id"), nullable=False
    )
    value = db.Column(db.Numeric(20, 2), nullable=False)

    period = db.relationship("Period", back_populates="values")
    metric = db.relationship("Metric")

    __table_args__ = (
        db.UniqueConstraint("period_id", "metric_id"),
    )


class CourtCase(db.Model):
    __tablename__ = "court_cases"
    id = db.Column(db.Integer, primary_key=True)
    monopoly_id = db.Column(
        db.Integer, db.ForeignKey("monopolies.id"), nullable=False
    )
    case_number = db.Column(db.String(100), nullable=False)
    court_name = db.Column(db.String(200), nullable=False)
    decision_date = db.Column(db.Date, nullable=True)
    decision_link = db.Column(db.String(500), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="pending")

    monopoly = db.relationship("Monopoly", back_populates="court_cases")


class CountryIndustryNote(db.Model):
    __tablename__ = "country_industry_notes"
    id = db.Column(db.Integer, primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey("countries.id", ondelete="CASCADE"), nullable=False)
    industry_id = db.Column(db.Integer, db.ForeignKey("industries.id", ondelete="CASCADE"), nullable=False)

    market_scope = db.Column(db.String(10), nullable=False, default="ru")

    title = db.Column(db.String(200), nullable=True)
    body = db.Column(db.Text, nullable=False, default="")
    hhi_override = db.Column(db.Float, nullable=True)
    top_share_override = db.Column(db.Float, nullable=True)
    companies_override = db.Column(db.Integer, nullable=True)

    country = db.relationship("Country")
    industry = db.relationship("Industry")

    __table_args__ = (
        db.UniqueConstraint("country_id", "industry_id", "market_scope"),
        db.Index("ix_note_country_industry", "country_id", "industry_id", "market_scope"),
    )

    def __repr__(self):
        return f"<Note {self.country_id}/{self.industry_id}>"


class Market(db.Model):
    __tablename__ = "markets"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    industry_id = db.Column(
        db.Integer, db.ForeignKey("industries.id"), nullable=False
    )
    market_scope = db.Column(db.String(10), nullable=False, default="ru")
    country_id = db.Column(
        db.Integer, db.ForeignKey("countries.id"), nullable=True
    )
    hhi = db.Column(db.Float, nullable=True)
    monopoly_type_id = db.Column(
        db.Integer, db.ForeignKey("monopoly_types.id"), nullable=True
    )
    risks = db.Column(db.Text, nullable=True)

    industry = db.relationship("Industry", back_populates="markets")
    country = db.relationship("Country")
    monopoly_type = db.relationship("MonopolyType")
    entries = db.relationship(
        "MonopolyMarket", back_populates="market",
        lazy=True, cascade="all, delete-orphan",
    )

    __table_args__ = (
        db.UniqueConstraint("industry_id", "name", "market_scope", "country_id"),
    )

    def __repr__(self):
        return f"<Market {self.name}>"

    def __str__(self):
        return self.name


class MonopolyMarket(db.Model):
    __tablename__ = "monopoly_markets"
    id = db.Column(db.Integer, primary_key=True)
    monopoly_id = db.Column(
        db.Integer, db.ForeignKey("monopolies.id"), nullable=False
    )
    market_id = db.Column(
        db.Integer, db.ForeignKey("markets.id"), nullable=False
    )
    share = db.Column(db.Float, nullable=False)
    is_main = db.Column(db.Boolean, nullable=False, default=False)

    monopoly = db.relationship("Monopoly", back_populates="market_entries")
    market = db.relationship("Market", back_populates="entries")

    __table_args__ = (
        db.UniqueConstraint("monopoly_id", "market_id"),
    )

    def __repr__(self):
        return f"<MonopolyMarket {self.monopoly_id}/{self.market_id}>"
