wsgi_app = "app.main:app"
worker_class = "uvicorn.workers.UvicornWorker"
pidfile = "/tmp/apps.pid"
max_requests = 5000


bind = "0.0.0.0:8000"
workers = 4
