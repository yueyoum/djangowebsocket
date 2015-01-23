# -*- coding: utf-8 -*-

__author__ = 'Wang Chao'
__date__ = '15-1-23'

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")

from djangowebsocket.wsgi import get_wsgi_application
application = get_wsgi_application()
