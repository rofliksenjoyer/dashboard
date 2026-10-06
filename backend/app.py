import os
from flask import (
    Flask, render_template, jsonify, request, abort,
    redirect, url_for, flash
)
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user
)
from wtforms.validators import DataRequired

from config import Config
from extensions import db, migrate
from models import (
    Industry, Monopoly, Period, PeriodValue, Metric, CourtCase
)
from seed import seed_metrics, seed_industries
from wtforms import SelectField


app = Flask(__name__, template_folder="templates", static_folder="../static")
app.config.from_object(Config)
db.init_app(app)
migrate.init_app(app, db)


# ---------- Авторизация ----------
class AdminUser(UserMixin):
    def __init__(self, id):
        self.id = id


ADMIN_LOGIN = os.getenv("ADMIN_LOGIN", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")


login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    if user_id == "admin":
        return AdminUser("admin")
    return None


# ---------- Расчёты ----------
def get_metric_value(period, code):
    m = Metric.query.filter_by(code=code).first()
    if not m:
        return None
    v = PeriodValue.query.filter_by(
        period_id=period.id, metric_id=m.id
    ).first()
    return float(v.value) if v else None


def calculate_ratios(period):
    revenue = get_metric_value(period, "revenue")
    net_profit = get_metric_value(period, "net_profit")
    assets = get_metric_value(period, "assets")
    equity = get_metric_value(period, "equity")
    credits = get_metric_value(period, "credits")

    ratios = {}
    try:
        if revenue and net_profit is not None:
            ratios["profitability"] = round(net_profit / revenue * 100, 2)
            ratios["lerner"] = round(net_profit / revenue, 4)
        if equity and net_profit is not None:
            ratios["roe"] = round(net_profit / equity * 100, 2)
        if assets and equity:
            ratios["autonomy"] = round(equity / assets, 2)
        if equity and credits:
            ratios["debt_load"] = round(credits / equity, 2)
    except ZeroDivisionError:
        pass
    return ratios


def calculate_hhi(industry_id, year):
    monopolies = Monopoly.query.filter_by(industry_id=industry_id).all()
    revenues = []
    for m in monopolies:
        period = Period.query.filter_by(
            monopoly_id=m.id, year=year
        ).first()
        if period:
            rev = get_metric_value(period, "revenue")
            if rev:
                revenues.append(rev)
    if not revenues:
        return None
    total = sum(revenues)
    return round(sum((r / total * 100) ** 2 for r in revenues), 2)


def calculate_market_shares(industry_id, year):
    """
    Доли рынка всех компаний отрасли за указанный год (в процентах).
    Возвращает список: {'name', 'revenue', 'share'}.
    """
    monopolies = Monopoly.query.filter_by(industry_id=industry_id).all()
    rows = []
    for m in monopolies:
        period = Period.query.filter_by(
            monopoly_id=m.id, year=year
        ).first()
        if not period:
            continue
        revenue = get_metric_value(period, "revenue")
        if revenue:
            rows.append({"name": m.name, "revenue": revenue})

    total = sum(r["revenue"] for r in rows)
    if not total:
        return []

    for r in rows:
        r["share"] = round(r["revenue"] / total * 100, 2)

    rows.sort(key=lambda r: r["revenue"], reverse=True)
    return rows


# ---------- Логин / логаут ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_ = request.form.get("login")
        password = request.form.get("password")
        if login_ == ADMIN_LOGIN and password == ADMIN_PASSWORD:
            login_user(AdminUser("admin"))
            return redirect(request.args.get("next") or "/admin/")
        flash("Неверный логин или пароль", "error")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


# ---------- Публичные маршруты ----------
@app.route("/")
def index():
    type_filter = request.args.get("type")
    industry_filter = request.args.get("industry")
    search = request.args.get("q", "").strip()

    query = Industry.query

    if industry_filter and industry_filter.isdigit():
        query = query.filter_by(id=int(industry_filter))

    industries = query.all()

    grouped = {}
    for industry in industries:
        m_query = Monopoly.query.filter_by(industry_id=industry.id)
        if type_filter in ("natural", "artificial"):
            m_query = m_query.filter_by(monopoly_type=type_filter)
        if search:
            m_query = m_query.filter(
                db.or_(
                    Monopoly.name.ilike(f"%{search}%"),
                    Monopoly.inn.ilike(f"%{search}%"),
                )
            )
        monopolies = m_query.all()
        if monopolies:
            grouped[industry.name] = {
                "monopolies": monopolies,
            }

    all_industries = Industry.query.order_by(Industry.name).all()

    return render_template(
        "index.html",
        grouped=grouped,
        current_filter=type_filter,
        current_industry=industry_filter,
        all_industries=all_industries,
        search=search,
    )


@app.route("/monopoly/<int:monopoly_id>")
def monopoly_detail(monopoly_id):
    m = Monopoly.query.get_or_404(monopoly_id)
    periods = (
        Period.query.filter_by(monopoly_id=monopoly_id)
        .order_by(Period.year)
        .all()
    )

    chart_data = []
    for p in periods:
        ratios = calculate_ratios(p)
        hhi_year = calculate_hhi(m.industry_id, p.year)
        chart_data.append({
            "period": str(p.year),
            "revenue": get_metric_value(p, "revenue"),
            "net_profit": get_metric_value(p, "net_profit"),
            "assets": get_metric_value(p, "assets"),
            "equity": get_metric_value(p, "equity"),
            "ratios": ratios,
            "hhi": hhi_year,
        })

    latest = chart_data[-1] if chart_data else None

    court_cases = CourtCase.query.filter_by(monopoly_id=monopoly_id).all()

    hhi = None
    market_shares = []
    market_share = None
    if periods:
        latest_year = periods[-1].year
        hhi = calculate_hhi(m.industry_id, latest_year)
        market_shares = calculate_market_shares(m.industry_id, latest_year)
        for row in market_shares:
            if row["name"] == m.name:
                market_share = row["share"]
                break

    return render_template(
        "monopoly.html",
        monopoly=m,
        chart_data=chart_data,
        latest=latest,
        court_cases=court_cases,
        hhi=hhi,
        market_shares=market_shares,
        market_share=market_share,
    )


# ---------- API ----------
@app.route("/api/monopolies")
def api_monopolies():
    type_filter = request.args.get("type")
    industry_filter = request.args.get("industry")

    query = Monopoly.query
    if type_filter in ("natural", "artificial"):
        query = query.filter(Monopoly.monopoly_type == type_filter)
    if industry_filter and industry_filter.isdigit():
        query = query.filter(Monopoly.industry_id == int(industry_filter))

    return jsonify([
        {
            "id": m.id, "name": m.name, "inn": m.inn,
            "industry": m.industry.name,
            "monopoly_type": m.monopoly_type,
        }
        for m in query.all()
    ])


@app.route("/api/monopoly/<int:monopoly_id>/data")
def api_monopoly_data(monopoly_id):
    periods = (
        Period.query.filter_by(monopoly_id=monopoly_id)
        .order_by(Period.year)
        .all()
    )
    return jsonify([
        {
            "period": str(p.year),
            "ratios": calculate_ratios(p),
        }
        for p in periods
    ])


@app.route("/api/hhi/<int:industry_id>")
def api_hhi(industry_id):
    year_str = request.args.get("year")
    if not year_str:
        abort(400, "year обязателен")
    year = int(year_str)
    return jsonify({"hhi": calculate_hhi(industry_id, year)})


@app.route("/api/market-shares/<int:industry_id>")
def api_market_shares(industry_id):
    year_str = request.args.get("year")
    if not year_str:
        abort(400, "year обязателен")
    year = int(year_str)
    return jsonify(calculate_market_shares(industry_id, year))


# ---------- Flask-Admin ----------
class SecureAdminIndexView(AdminIndexView):
    @expose("/")
    @login_required
    def index(self):
        return super().index()


class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login", next=request.url))


class IndustryAdmin(SecureModelView):
    column_list = ("id", "name")
    form_columns = ("name",)
    column_labels = {
        "name": "Название отрасли",
    }
    form_args = {
        "name": {"validators": [DataRequired()]},
    }


from wtforms import SelectField


class MonopolyAdmin(SecureModelView):
    column_list = ("id", "name", "inn", "industry", "monopoly_type_label", "website")
    form_columns = ("name", "inn", "industry", "monopoly_type", "description", "website")
    column_labels = {
        "name": "Название",
        "inn": "ИНН",
        "industry": "Отрасль",
        "monopoly_type": "Тип монополии",
        "monopoly_type_label": "Тип монополии",
        "description": "Описание",
        "website": "Сайт",
    }

    # Список допустимых значений в выпадающем списке
    form_choices = {
        "monopoly_type": [
            ("natural", "Естественная"),
            ("artificial", "Искусственная"),
        ]
    }

    form_args = {
        "name": {"validators": [DataRequired()]},
        "inn": {"validators": [DataRequired()]},
        "industry": {"validators": [DataRequired()]},
        "monopoly_type": {"validators": [DataRequired()]},
    }

    # Чтобы в column_list отображалась русская подпись, а не natural/artificial
    @property
    def _type_labels(self):
        return {"natural": "Естественная", "artificial": "Искусственная"}

    def _monopoly_type_label_formatter(self, context, model, name):
        return self._type_labels.get(model.monopoly_type, model.monopoly_type)

    column_formatters = {
        "monopoly_type_label": _monopoly_type_label_formatter,
    }


class PeriodValueInline(object):
    """Инлайн для финансовых показателей внутри годового периода."""
    model = PeriodValue
    form_columns = ["id", "metric", "value"]
    column_list = ["metric", "value"]


class PeriodAdmin(SecureModelView):
    column_list = ("id", "monopoly", "year")
    form_columns = ("monopoly", "year", "values")
    column_labels = {
        "monopoly": "Монополия",
        "year": "Год",
        "values": "Финансовые показатели",
    }
    inline_models = [PeriodValueInline]
    form_args = {
        "monopoly": {"validators": [DataRequired()]},
        "year": {"validators": [DataRequired()]},
    }


class MetricAdmin(SecureModelView):
    column_list = ("id", "name", "code", "unit")
    form_columns = ("code", "name", "unit")
    column_labels = {
        "code": "Код (служебный)",
        "name": "Название показателя",
        "unit": "Единица измерения",
    }


class CourtCaseAdmin(SecureModelView):
    column_list = (
        "id", "monopoly", "case_number", "court_name",
        "decision_date", "status"
    )
    form_columns = (
        "monopoly", "case_number", "court_name",
        "decision_date", "decision_link", "summary", "status"
    )
    column_labels = {
        "monopoly": "Монополия",
        "case_number": "Номер дела",
        "court_name": "Суд",
        "decision_date": "Дата решения",
        "decision_link": "Ссылка на решение",
        "summary": "Краткое описание",
        "status": "Статус (won / lost / pending)",
    }
    form_args = {
        "monopoly": {"validators": [DataRequired()]},
        "case_number": {"validators": [DataRequired()]},
        "court_name": {"validators": [DataRequired()]},
    }


admin = Admin(
    app, name="Панель администратора",
    template_mode="bootstrap4", index_view=SecureAdminIndexView()
)
admin.add_view(IndustryAdmin(Industry, db.session, name="Отрасли"))
admin.add_view(MonopolyAdmin(Monopoly, db.session, name="Монополии"))
admin.add_view(PeriodAdmin(Period, db.session, name="Периоды отчётности"))
admin.add_view(MetricAdmin(Metric, db.session, name="Справочник показателей"))
admin.add_view(CourtCaseAdmin(CourtCase, db.session, name="Судебные дела"))


# ---------- CLI ----------
@app.cli.command("seed")
def seed_command():
    seed_metrics()
    seed_industries()
    print("Справочники заполнены.")


@app.cli.command("reset-db")
def reset_db_command():
    confirm = input("Это удалит все данные. Введите 'yes': ")
    if confirm != "yes":
        print("Отменено.")
        return
    db.drop_all()
    db.create_all()
    print("БД пересоздана.")


if __name__ == "__main__":
    app.run(debug=True)