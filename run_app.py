import os
import sys
import shutil
import socket
import time
import threading

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

import traceback


def _log_exception(exc_type, exc_value, exc_tb):
    try:
        if getattr(sys, "frozen", False):
            base = os.path.dirname(os.path.abspath(sys.executable))
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base, "error.log"), "a", encoding="utf-8") as f:
            traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
    except Exception:
        pass


sys.excepthook = _log_exception

FROZEN = getattr(sys, "frozen", False)
if FROZEN:
    RES = sys._MEIPASS
    EXE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    RES = os.path.dirname(os.path.abspath(__file__))
    EXE_DIR = RES
    sys.path.insert(0, RES)
    os.chdir(RES)

TEMPLATES = os.path.join(RES, "templates")
STATIC = os.path.join(RES, "static")

db_file = os.path.join(EXE_DIR, "monopolies.db")
if not os.path.exists(db_file) and FROZEN:
    bundled = os.path.join(sys._MEIPASS, "data", "monopolies.db")
    if os.path.exists(bundled):
        shutil.copy(bundled, db_file)

os.environ["DATABASE_URL"] = "sqlite:///" + os.path.abspath(db_file).replace("\\", "/")

from app import app
from extensions import db

app.template_folder = TEMPLATES
app.static_folder = STATIC
app.static_url_path = "/static"
app.__dict__.pop("jinja_loader", None)

with app.app_context():
    db.create_all()

HOST = "127.0.0.1"
PORT = 5000


def start_server():
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)


def wait_for_server(host, port, timeout=15.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.1)
    return False


threading.Thread(target=start_server, daemon=True).start()
if not wait_for_server(HOST, PORT):
    sys.exit(1)

import webview

webview.create_window(
    "Мониторинг монополий",
    f"http://{HOST}:{PORT}",
    width=1280,
    height=800,
    min_size=(900, 600),
)
webview.start()
