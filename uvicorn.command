871b99d6cbbe327a237b690502d069ec_venv/bin/gunicorn \
-w 1 -k uvicorn.workers.UvicornWorker app.main:app \
--bind 0.0.0.0:8000 \
--daemon