"""Gunicorn configuration for production"""
import multiprocessing
import os

# Server socket
# Render sets PORT automatically, ensure it's converted to int
port = int(os.environ.get('PORT', 5000))
bind = f"0.0.0.0:{port}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.environ.get('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'tuitiontrack'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_redirect = False

# SSL (if needed)
# keyfile = None
# certfile = None

def when_ready(server):
    """Called just after the server is started"""
    server.log.info("Server is ready. Spawning workers")

def on_exit(server):
    """Called just before exiting"""
    server.log.info("Shutting down: Master")

