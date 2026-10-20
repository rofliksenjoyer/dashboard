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
    Country, Industry, Monopoly, Period, PeriodValue, Metric, CourtCase
)
from seed import seed_all
import services
from services import VALID_SCOPES


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


@app.route("/scope/<scope>")
def scope_view(scope):
    if scope not in VALID_SCOPES:
        abort(404)
    return render_template("scope.html", scope=scope)


@app.route("/scope/<scope>/industry/<int:industry_id>")
def sector_view(scope, industry_id):
    if scope not in VALID_SCOPES:
        abort(404)
    ind = Industry.query.get(industry_id)
    if not ind:
        abort(404)
    return render_template(
        "sector.html", scope=scope,
        industry_id=industry_id, industry_name=ind.name,
    )


@app.route("/company/<int:monopoly_id>")
def company_passport(monopoly_id):
    m = Monopoly.query.get(monopoly_id)
    if not m:
        abort(404)
    return render_template(
        "passport.html",
        monopoly_id=m.id, monopoly_name=m.name,
    )


# ---------- API ----------
def api_response(data, meta=None, status=200):
    payload = {"data": data}
    if meta is not None:
        payload["meta"] = meta
    return jsonify(payload), status


def api_error(message, status=400):
    return jsonify({"error": message}), status


@app.route("/api/years")
def api_years():
    return api_response(services.available_years())


@app.route("/api/scopes/<scope>")
def api_scope(scope):
    if scope not in VALID_SCOPES:
        return api_error("Неизвестный контур", 404)
    year = request.args.get("year", type=int)
    return api_response(services.get_scope_overview(scope, year))


@app.route("/api/scopes/<scope>/industries/<int:industry_id>")
def api_sector(scope, industry_id):
    if scope not in VALID_SCOPES:
        return api_error("Неизвестный контур", 404)
    year = request.args.get("year", type=int)
    data = services.get_sector_detail(scope, industry_id, year)
    if not data:
        return api_error("Отрасль не найдена", 404)
    return api_response(data)


@app.route("/api/monopolies/<int:monopoly_id>")
def api_monopoly(monopoly_id):
    data = services.get_company_passport(monopoly_id)
    if not data:
        return api_error("Монополия не найдена", 404)
    return api_response(data)


@app.route("/api/monopolies")
def api_monopolies():
    type_filter = request.args.get("type")
    industry_filter = request.args.get("industry")
    country_filter = request.args.get("country")
    search = request.args.get("q", "").strip()
    limit = request.args.get("limit", type=int)
    offset = request.args.get("offset", 0, type=int)

    query = Monopoly.query
    if type_filter in ("natural", "artificial"):
        query = query.filter(Monopoly.monopoly_type == type_filter)
    if industry_filter and industry_filter.isdigit():
        query = query.filter(Monopoly.industry_id == int(industry_filter))
    if country_filter and country_filter.isdigit():
        query = query.filter(Monopoly.country_id == int(country_filter))
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
            "short_name": m.short_name,
            "inn": m.inn,
            "monopoly_type": m.monopoly_type,
            "badge_type": m.badge_type,
            "industry": {"id": m.industry.id, "name": m.industry.name},
            "country": {"id": m.country.id, "name": m.country.name, "code": m.country.code},
            "website": m.website,
        }
        for m in query.all()
    ]

    return api_response(data, meta={"total": total, "limit": limit, "offset": offset})


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


class CountryAdmin(SecureModelView):
    column_list = ("id", "name", "code", "market_scope")
    form_columns = ("name", "code", "market_scope")
    column_labels = {
        "name": "Название страны",
        "code": "Код (ISO)",
        "market_scope": "Контур (ru / world)",
    }
    form_args = {
        "name": {"validators": [DataRequired()]},
        "code": {"validators": [DataRequired()]},
        "market_scope": {"validators": [DataRequired()]},
    }
    form_choices = {
        "market_scope": [("ru", "Национальный (RU)"), ("world", "Мировой (World)")]
    }


class IndustryAdmin(SecureModelView):
    column_list = ("id", "name")
    form_columns = ("name",)
    column_labels = {"name": "Название отрасли"}
    form_args = {"name": {"validators": [DataRequired()]}}


class MonopolyAdmin(SecureModelView):
    column_list = (
        "id", "name", "short_name", "inn", "country", "industry",
        "monopoly_type", "badge_type", "employees", "founded_year"
    )
    form_columns = (
        "name", "short_name", "inn", "color", "country", "industry",
        "monopoly_type", "badge_type", "activity", "description",
        "website", "employees", "founded_year", "hq"
    )
    column_labels = {
        "name": "Название",
        "short_name": "Короткое имя",
        "inn": "ИНН",
        "color": "Цвет (hex)",
        "country": "Страна",
        "industry": "Отрасль",
        "monopoly_type": "Тип монополии",
        "badge_type": "Бейдж",
        "activity": "Деятельность",
        "description": "Описание",
        "website": "Сайт",
        "employees": "Сотрудников, тыс.",
        "founded_year": "Год основания",
        "hq": "Штаб-квартира",
    }
    form_choices = {
        "monopoly_type": [
            ("natural", "Естественная"),
            ("artificial", "Искусственная"),
        ],
        "badge_type": [
            ("natural", "Естественная"),
            ("resource", "Ресурсная"),
            ("platform", "Платформенная"),
            ("hightech", "Высокотехнологичная"),
        ],
    }
    form_args = {
        "name": {"validators": [DataRequired()]},
        "inn": {"validators": [DataRequired()]},
        "country": {"validators": [DataRequired()]},
        "industry": {"validators": [DataRequired()]},
        "monopoly_type": {"validators": [DataRequired()]},
    }


class PeriodValueInline(object):
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
admin.add_view(CountryAdmin(Country, db.session, name="Страны"))
admin.add_view(IndustryAdmin(Industry, db.session, name="Отрасли"))
admin.add_view(MonopolyAdmin(Monopoly, db.session, name="Монополии"))
admin.add_view(PeriodAdmin(Period, db.session, name="Периоды отчётности"))
admin.add_view(MetricAdmin(Metric, db.session, name="Справочник показателей"))
admin.add_view(CourtCaseAdmin(CourtCase, db.session, name="Судебные дела"))


# ---------- CLI ----------
@app.cli.command("seed-all")
def seed_all_command():
    seed_all()
    print("База заполнена.")


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