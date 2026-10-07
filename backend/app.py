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
    return render_template("index.html")

@app.route("/monopoly/<int:monopoly_id>")
def monopoly_detail(monopoly_id):
    m = Monopoly.query.get(monopoly_id)
    if not m:
        abort(404)
    return render_template("monopoly.html", monopoly_id=m.id, monopoly_name=m.name)

# ---------- API ----------
from flask import jsonify, request, abort


def api_response(data, meta=None, status=200):
    payload = {"data": data}
    if meta is not None:
        payload["meta"] = meta
    return jsonify(payload), status


def api_error(message, status=400):
    return jsonify({"error": message}), status


# --- Справочник метрик ---
@app.route("/api/metrics")
def api_metrics():
    metrics = Metric.query.order_by(Metric.name).all()
    data = [
        {
            "id": m.id,
            "code": m.code,
            "name": m.name,
            "unit": m.unit,
        }
        for m in metrics
    ]
    return api_response(data)


# --- Отрасли ---
@app.route("/api/industries")
def api_industries():
    industries = Industry.query.order_by(Industry.name).all()
    data = [
        {
            "id": i.id,
            "name": i.name,
            "monopolies_count": len(i.monopolies),
        }
        for i in industries
    ]
    return api_response(data)


@app.route("/api/industries/<int:industry_id>")
def api_industry(industry_id):
    industry = Industry.query.get(industry_id)
    if not industry:
        return api_error("Отрасль не найдена", 404)

    monopolies = [
        {
            "id": m.id,
            "name": m.name,
            "inn": m.inn,
            "monopoly_type": m.monopoly_type,
        }
        for m in industry.monopolies
    ]

    return api_response({
        "id": industry.id,
        "name": industry.name,
        "monopolies": monopolies,
    })


@app.route("/api/industries/<int:industry_id>/hhi")
def api_industry_hhi(industry_id):
    year_str = request.args.get("year")
    if not year_str or not year_str.isdigit():
        return api_error("Параметр year обязателен и должен быть числом")

    industry = Industry.query.get(industry_id)
    if not industry:
        return api_error("Отрасль не найдена", 404)

    year = int(year_str)
    hhi = calculate_hhi(industry_id, year)
    return api_response({
        "industry_id": industry_id,
        "year": year,
        "hhi": hhi,
    })


@app.route("/api/industries/<int:industry_id>/market-shares")
def api_industry_market_shares(industry_id):
    year_str = request.args.get("year")
    if not year_str or not year_str.isdigit():
        return api_error("Параметр year обязателен и должен быть числом")

    industry = Industry.query.get(industry_id)
    if not industry:
        return api_error("Отрасль не найдена", 404)

    year = int(year_str)
    shares = calculate_market_shares(industry_id, year)
    total_revenue = sum(r["revenue"] for r in shares) if shares else 0

    return api_response(
        shares,
        meta={
            "industry_id": industry_id,
            "industry_name": industry.name,
            "year": year,
            "total_revenue": total_revenue,
            "companies_count": len(shares),
        },
    )


# --- Монополии ---
@app.route("/api/monopolies")
def api_monopolies():
    type_filter = request.args.get("type")
    industry_filter = request.args.get("industry")
    search = request.args.get("q", "").strip()
    limit = request.args.get("limit", type=int)
    offset = request.args.get("offset", 0, type=int)

    query = Monopoly.query
    if type_filter in ("natural", "artificial"):
        query = query.filter(Monopoly.monopoly_type == type_filter)
    if industry_filter and industry_filter.isdigit():
        query = query.filter(Monopoly.industry_id == int(industry_filter))
    if search:
        query = query.filter(
            db.or_(
                Monopoly.name.ilike(f"%{search}%"),
                Monopoly.inn.ilike(f"%{search}%"),
            )
        )

    total = query.count()
    if limit:
        query = query.limit(limit).offset(offset)

    data = [
        {
            "id": m.id,
            "name": m.name,
            "inn": m.inn,
            "monopoly_type": m.monopoly_type,
            "industry": {
                "id": m.industry.id,
                "name": m.industry.name,
            },
            "website": m.website,
        }
        for m in query.all()
    ]

    return api_response(
        data,
        meta={
            "total": total,
            "limit": limit,
            "offset": offset,
        },
    )


@app.route("/api/monopolies/<int:monopoly_id>")
def api_monopoly(monopoly_id):
    m = Monopoly.query.get(monopoly_id)
    if not m:
        return api_error("Монополия не найдена", 404)

    periods = (
        Period.query.filter_by(monopoly_id=monopoly_id)
        .order_by(Period.year)
        .all()
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
        periods_data.append({
            "year": p.year,
            "values": values,
            "ratios": calculate_ratios(p),
            "hhi": calculate_hhi(m.industry_id, p.year),
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

    return api_response({
        "id": m.id,
        "name": m.name,
        "inn": m.inn,
        "monopoly_type": m.monopoly_type,
        "description": m.description,
        "website": m.website,
        "industry": {
            "id": m.industry.id,
            "name": m.industry.name,
        },
        "periods": periods_data,
        "court_cases": court_cases,
    })


@app.route("/api/monopolies/<int:monopoly_id>/periods")
def api_monopoly_periods(monopoly_id):
    m = Monopoly.query.get(monopoly_id)
    if not m:
        return api_error("Монополия не найдена", 404)

    periods = (
        Period.query.filter_by(monopoly_id=monopoly_id)
        .order_by(Period.year)
        .all()
    )

    data = [
        {
            "id": p.id,
            "year": p.year,
            "values_count": len(p.values),
        }
        for p in periods
    ]
    return api_response(data, meta={"monopoly_id": monopoly_id, "monopoly_name": m.name})


@app.route("/api/monopolies/<int:monopoly_id>/periods/<int:year>")
def api_monopoly_period(monopoly_id, year):
    m = Monopoly.query.get(monopoly_id)
    if not m:
        return api_error("Монополия не найдена", 404)

    period = Period.query.filter_by(
        monopoly_id=monopoly_id, year=year
    ).first()
    if not period:
        return api_error(f"Период {year} не найден", 404)

    values = {}
    for pv in period.values:
        values[pv.metric.code] = {
            "name": pv.metric.name,
            "unit": pv.metric.unit,
            "value": float(pv.value),
        }

    return api_response({
        "monopoly_id": monopoly_id,
        "year": year,
        "values": values,
        "ratios": calculate_ratios(period),
        "hhi": calculate_hhi(m.industry_id, year),
    })


# --- Судебные дела ---
@app.route("/api/court-cases")
def api_court_cases():
    monopoly_filter = request.args.get("monopoly_id")
    status_filter = request.args.get("status")

    query = CourtCase.query
    if monopoly_filter and monopoly_filter.isdigit():
        query = query.filter(CourtCase.monopoly_id == int(monopoly_filter))
    if status_filter in ("won", "lost", "pending"):
        query = query.filter(CourtCase.status == status_filter)

    data = [
        {
            "id": c.id,
            "monopoly_id": c.monopoly_id,
            "monopoly_name": c.monopoly.name if c.monopoly else None,
            "case_number": c.case_number,
            "court_name": c.court_name,
            "decision_date": c.decision_date.isoformat() if c.decision_date else None,
            "decision_link": c.decision_link,
            "summary": c.summary,
            "status": c.status,
        }
        for c in query.order_by(CourtCase.id).all()
    ]
    return api_response(data, meta={"total": len(data)})

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