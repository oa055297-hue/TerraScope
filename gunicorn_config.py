
import os

bind = "0.0.0.0:5000"
workers = os.cpu_count() * 2 + 1 # Recommended number of workers
worker_class = "sync"
# accesslog = "-" # Log to stdout
# errorlog = "-" # Log to stdout
loglevel = "info"

# Path to the Flask application entry point
# Assuming your create_app() function is in src/main.py
wsgi_app = "src.main:create_app()"

