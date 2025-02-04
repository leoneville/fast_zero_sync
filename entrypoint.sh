#!/bin/sh

poetry run alembic upgrade head

poetry run gunicorn -w 13 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 fast_zero.app:app