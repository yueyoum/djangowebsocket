# -*- coding: utf-8 -*-

__author__ = 'Wang Chao'
__date__ = '15-1-9'

import gevent.monkey
gevent.monkey.patch_all()

import uwsgi

import django
from django.core.handlers.wsgi import WSGIHandler

class WebSocketApplication(WSGIHandler):
    def _fake_start_response(self, *args, **kwargs):
        pass

    def __call__(self, environ, start_response):
        uwsgi.websocket_handshake()
        return super(WebSocketApplication, self).__call__(environ, self._fake_start_response)


def get_wsgi_application():
    django.setup()
    return WebSocketApplication()

