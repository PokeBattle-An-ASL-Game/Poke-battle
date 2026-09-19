import os

bind = os.environ.get("POOKIE_BIND", "127.0.0.1:8000")
workers = int(os.environ.get("POOKIE_WORKERS", "2"))
timeout = 30
accesslog = None
errorlog = "-"
loglevel = "info"
limit_request_line = 4094
limit_request_fields = 50
