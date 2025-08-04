wsgi_app = "nickelodeon.wsgi:application"
preload_app = True
daemon = False
raw_env = ["DJANGO_SETTINGS_MODULE=nickelodeon.settings"]
workers = 2
threads = 1
max_requests = 300
max_requests_jitter = 20
