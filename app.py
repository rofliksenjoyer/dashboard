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
from wtforms.validators import DataRequired, Optional, URL
from wtforms import FloatField, IntegerField

from config import Config
from extensions import db, migrate
from models import (
    Country, Industry, MonopolyType, Monopoly, Period, PeriodValue,
    Metric, CourtCase, CountryIndustryNote, Market, MonopolyMarket,
)
from seed import seed_all
import services
from services import VALID_SCOPES


app = Flask(__name__, template_folder="templates", static_folder="../static")
app.config.from_object(Config)
db.init_app(app)
migrate.init_app(app, db)


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


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scope/<scope>")
def scope_view(scope):
    if scope not in VALID_SCOPES:
        abort(404)
    return render_template("scope.html", scope=scope, country_id=request.args.get("country", type=int))


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
        country_id=request.args.get("country", type=int)
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


@app.route("/api/monopoly-types")
def api_monopoly_types():
    return api_response([{"id": t.id, "name": t.name} for t in MonopolyType.query.all()])

@app.route("/api/totals")
def api_totals():
    return api_response(services.get_overall_totals())


@app.route("/api/scopes/<scope>/totals")
def api_scope_totals(scope):
    if scope not in VALID_SCOPES:
        return api_error("Неизвестный контур", 404)
    return api_response(services.get_global_totals(scope))

@app.route("/api/scopes/<scope>")
def api_scope(scope):
    if scope not in VALID_SCOPES:
        return api_error("Неизвестный контур", 404)
    year = request.args.get("year", type=int)
    country_id = request.args.get("country", type=int)
    return api_response(services.get_scope_overview(scope, country_id, year))


@app.route("/api/scopes/<scope>/industries/<int:industry_id>")
def api_sector(scope, industry_id):
    if scope not in VALID_SCOPES:
        return api_error("Неизвестный контур", 404)
    year = request.args.get("year", type=int)
    country_id = request.args.get("country", type=int)
    type_id = request.args.get("type", type=int)
    market_id = request.args.get("market", type=int)
    data = services.get_sector_detail(scope, industry_id, country_id, type_id, market_id, year)
    if not data:
        return api_error("Отрасль не найдена", 404)
    return api_response(data)


@app.route("/api/monopolies/<int:monopoly_id>")
def api_monopoly(monopoly_id):
    data = services.get_company_passport(monopoly_id)
    if not data:
        return api_error("Монополия не найдена", 404)
    return api_response(data)


@app.route("/api/markets/<int:market_id>")
def api_market(market_id):
    data = services.get_market_detail(market_id)
    if not data:
        return api_error("Рынок не найден", 404)
    return api_response(data)


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
    column_list = ("id", "name", "code", "currency")
    form_columns = ("name", "code", "currency")
    column_labels = {
        "name": "Название страны",
        "code": "Код (ISO)",
        "currency": "Валюта отчётности (RUB, USD...)",
    }
    form_args = {
        "name": {"validators": [DataRequired()]},
        "code": {"validators": [DataRequired()]},
    }


class IndustryAdmin(SecureModelView):
    column_list = ("id", "name")
    form_columns = ("name",)
    column_labels = {"name": "Название отрасли"}
    form_args = {"name": {"validators": [DataRequired()]}}


class MonopolyTypeAdmin(SecureModelView):
    column_list = ("id", "name")
    form_columns = ("name",)
    column_labels = {"name": "Название типа"}
    form_args = {"name": {"validators": [DataRequired()]}}


class MonopolyAdmin(SecureModelView):
    column_list = (
        "id", "name", "short_name", "inn", "country", "industry",
        "market_scope", "employees", "founded_year"
    )
    form_columns = (
        "name", "short_name", "inn",
        "country", "industry", "market_scope",
        "description", "website",
        "employees", "founded_year",
        "logo_url",
    )
    column_labels = {
        "name": "Название",
        "short_name": "Короткое имя",
        "inn": "ИНН",
        "country": "Страна",
        "industry": "Отрасль",
        "market_scope": "Контур рынка",
        "description": "Описание",
        "website": "Сайт",
        "employees": "Сотрудников, тыс.",
        "founded_year": "Год основания",
        "logo_url": "Ссылка на логотип (URL)",
    }
    form_choices = {
        "market_scope": [("ru", "Национальный"), ("world", "Глобальный")],
    }
    form_args = {
        "name": {"validators": [DataRequired()]},
        "inn": {"validators": [DataRequired()]},
        "country": {"validators": [DataRequired()]},
        "industry": {"validators": [DataRequired()]},
        "market_scope": {"validators": [DataRequired()]},
        "logo_url": {"validators": [Optional(), URL()]},
    }


class PeriodValueInline(object):
    model = PeriodValue
    form_columns = ["id", "metric", "value"]
    column_list = ["metric", "value"]


class PeriodAdmin(SecureModelView):
    column_list = ("id", "monopoly", "year")
    form_columns = ("monopoly", "year", "values")
    column_labels = {
        "monopoly": "Монополия", "year": "Год",
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
        "code": "Код (служебный)", "name": "Название показателя",
        "unit": "Единица измерения",
    }


COURT_STATUS_LABELS = {
    "won": "Выиграно",
    "lost": "Проиграно",
    "pending": "Рассматривается",
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
        "monopoly": "Монополия", "case_number": "Номер дела",
        "court_name": "Суд", "decision_date": "Дата решения",
        "decision_link": "Ссылка на решение", "summary": "Краткое описание",
        "status": "Статус",
    }
    column_formatters = {
        "status": lambda v, c, model, name: COURT_STATUS_LABELS.get(model.status, model.status),
    }
    form_choices = {
        "status": [
            ("won", "Выиграно"),
            ("lost", "Проиграно"),
            ("pending", "Рассматривается"),
        ],
    }
    form_args = {
        "monopoly": {"validators": [DataRequired()]},
        "case_number": {"validators": [DataRequired()]},
        "court_name": {"validators": [DataRequired()]},
    }


class CountryIndustryNoteAdmin(SecureModelView):
    column_list = (
        "id", "market_scope", "country", "industry", "title",
        "hhi_override", "top_share_override", "companies_override"
    )
    form_columns = (
        "market_scope", "country", "industry", "title", "body",
        "hhi_override", "top_share_override", "companies_override"
    )
    column_labels = {
        "market_scope": "Контур рынка",
        "country": "Страна",
        "industry": "Отрасль",
        "title": "Заголовок",
        "body": "Текст о монополизации",
        "hhi_override": "HHI вручную",
        "top_share_override": "Доля лидера, %",
        "companies_override": "Компаний",
    }
    form_choices = {
        "market_scope": [("ru", "Национальный"), ("world", "Глобальный")],
    }

    form_extra_fields = {
        "hhi_override": FloatField("HHI вручную", validators=[Optional()]),
        "top_share_override": FloatField("Доля лидера, %", validators=[Optional()]),
        "companies_override": IntegerField("Компаний (вручную)", validators=[Optional()]),
    }

    form_args = {
        "country": {"validators": [DataRequired()]},
        "industry": {"validators": [DataRequired()]},
        "body": {"validators": [DataRequired()]},
        "market_scope": {"validators": [DataRequired()]},
    }


class MarketAdmin(SecureModelView):
    column_list = ("id", "name", "industry", "market_scope", "country", "hhi", "monopoly_type")
    form_columns = ("name", "industry", "market_scope", "country", "hhi", "monopoly_type", "risks")
    column_labels = {
        "name": "Название рынка",
        "industry": "Отрасль",
        "market_scope": "Контур рынка",
        "country": "Страна (для национального)",
        "hhi": "HHI (вручную)",
        "monopoly_type": "Тип монополии рынка",
        "risks": "Чем грозит монополизация",
    }
    form_choices = {
        "market_scope": [("ru", "Национальный"), ("world", "Глобальный")],
    }
    form_args = {
        "name": {"validators": [DataRequired()]},
        "industry": {"validators": [DataRequired()]},
        "market_scope": {"validators": [DataRequired()]},
        "country": {"validators": [Optional()]},
        "hhi": {"validators": [Optional()]},
        "monopoly_type": {"validators": [Optional()]},
        "risks": {"validators": [Optional()]},
    }


class MonopolyMarketAdmin(SecureModelView):
    column_list = ("id", "monopoly", "market", "share", "is_main")
    form_columns = ("monopoly", "market", "share", "is_main")
    column_labels = {
        "monopoly": "Монополия",
        "market": "Рынок",
        "share": "Доля рынка, %",
        "is_main": "Главный рынок",
    }
    form_args = {
        "monopoly": {"validators": [DataRequired()]},
        "market": {"validators": [DataRequired()]},
        "share": {"validators": [DataRequired()]},
    }


admin = Admin(
    app, name="Панель администратора",
    template_mode="bootstrap4", index_view=SecureAdminIndexView()
)
admin.add_view(CountryAdmin(Country, db.session, name="Страны"))
admin.add_view(IndustryAdmin(Industry, db.session, name="Отрасли"))
admin.add_view(MonopolyTypeAdmin(MonopolyType, db.session, name="Типы монополий"))
admin.add_view(MonopolyAdmin(Monopoly, db.session, name="Монополии"))
admin.add_view(PeriodAdmin(Period, db.session, name="Периоды отчётности"))
admin.add_view(MetricAdmin(Metric, db.session, name="Справочник показателей"))
admin.add_view(CourtCaseAdmin(CourtCase, db.session, name="Судебные дела"))
admin.add_view(CountryIndustryNoteAdmin(
    CountryIndustryNote, db.session, name="Заметки по странам и отраслям"
))
admin.add_view(MarketAdmin(Market, db.session, name="Рынки (внутри отраслей)"))
admin.add_view(MonopolyMarketAdmin(MonopolyMarket, db.session, name="Доли компаний на рынках"))


@app.cli.command("seed-all")
def seed_all_command():
    seed_all()
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
