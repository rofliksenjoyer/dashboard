from extensions import db


class Industry(db.Model):
    __tablename__ = "industries"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    monopoly_type = db.Column(db.String(20), nullable=False)  # natural / artificial

    monopolies = db.relationship(
        "Monopoly", back_populates="industry",
        lazy=True, cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Industry {self.name}>"


class Monopoly(db.Model):
    __tablename__ = "monopolies"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    inn = db.Column(db.String(12), unique=True, nullable=False)
    industry_id = db.Column(
        db.Integer, db.ForeignKey("industries.id"), nullable=False
    )
    description = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(200), nullable=True)

    industry = db.relationship("Industry", back_populates="monopolies")
    periods = db.relationship(
        "Period", back_populates="monopoly",
        lazy=True, cascade="all, delete-orphan",
    )
    court_cases = db.relationship(
        "CourtCase", back_populates="monopoly",
        lazy=True, cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Monopoly {self.name}>"


class Period(db.Model):
    """Годовой период отчётности."""
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
    )


class Metric(db.Model):
    """Справочник финансовых показателей из отчётности."""
    __tablename__ = "metrics"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    unit = db.Column(db.String(20), nullable=True)

    values = db.relationship("PeriodValue", back_populates="metric")

    def __repr__(self):
        return f"<Metric {self.name}>"

    def __str__(self):
        return self.name  # чтобы в выпадающем списке был название, а не код


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