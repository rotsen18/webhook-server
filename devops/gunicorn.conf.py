import multiprocessing

bind = '0.0.0.0:5100'
workers = multiprocessing.cpu_count() * 2 + 1
forwarded_allow_ips = '*'
max_requests = 50
max_requests_jitter = 20
timeout = 120
access_log_format = '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
accesslog = '/var/log/webhook_server_access.log'
errorlog = '/var/log/webhook_server_error.log'
worker_class = 'gevent'
loglevel = 'debug'
