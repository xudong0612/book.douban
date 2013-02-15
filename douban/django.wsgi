import os, sys

WSGI_FILE = os.path.abspath(__file__)

APACHE_DIR = os.path.dirname(WSGI_FILE)

PROJ_DIR = os.path.dirname(APACHE_DIR)

TOP_DIR = os.path.dirname(PROJ_DIR)

sys.path.append(TOP_DIR)

sys.path.append(PROJ_DIR)

os.environ['PYTHON_EGG_CACHE'] = '/tmp/python-eggs'

os.environ['DJANGO_SETTINGS_MODULE'] = 'douban.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
