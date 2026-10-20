#!/usr/bin/env bash
set -e

echo "==> Применяю миграции..."
cd backend
python -m flask db upgrade

echo "==> Заполняю справочники и данные..."
python -m flask seed-all

echo "==> Запускаю gunicorn..."
exec gunicorn --chdir . app:app --bind 0.0.0.0:$PORT