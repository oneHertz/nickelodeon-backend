wsgi_app = "nickelodeon.site.wsgi:application"
preload_app = True
daemon = False
raw_env = ["DJANGO_SETTINGS_MODULE=nickelodeon.site.settings"]
workers = 2
threads = 1
max_requests = 300
max_requests_jitter = 20
