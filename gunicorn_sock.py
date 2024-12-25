bind = "unix:/home/www-data/flexify/myproject.sock"
workers = 3
worker_class = "sync"
timeout = 120
loglevel = "info"
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
