# -*- coding: utf-8 -*-

__author__ = 'Wang Chao'
__date__ = '15-1-9'

import logging

import uwsgi
import redis
from gevent import select

from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import classonlymethod


logger = logging.getLogger('django.websocket')

def _get_setting(key, default_value):
    return getattr(settings, key, default_value)

redis_client = redis.Redis(
        connection_pool=redis.ConnectionPool(
            host=_get_setting('WS_REDIS_HOST', '127.0.0.1'),
            port=_get_setting('WS_REDIS_PORT', 6379),
            db=_get_setting('WS_REDIS_DB', 0)
            )
        )

REDIS_GLOBAL_CHANNEL = _get_setting('WS_REDIS_GLOBAL_CHANNEL', 'DJWS-CHANNEL')
TIMEOUT = _get_setting('WS_WAIT_TIMEOUT', 10)


class WebSocketView(object):
    class WebSocketError(Exception):
        pass


    def __init__(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        self.redis = redis_client
        self.channel = self.redis.pubsub()
        self.channel.subscribe(REDIS_GLOBAL_CHANNEL)
        self.on_connect()


    def publish_global(self, text):
        print "PUBLISH GLOBAL", text
        self.redis.publish(REDIS_GLOBAL_CHANNEL, text)

    def recv(self):
        try:
            data = uwsgi.websocket_recv_nb()
            if data:
                self.on_websocket_data(data)
        except:
            raise self.WebSocketError()

    def send(self, text):
        uwsgi.websocket_send(text)

    def send_binary(self, binary_data):
        uwsgi.websocket_send_binary(binary_data)

    def on_connect(self):
        raise NotImplementedError()

    def on_connection_lost(self):
        raise NotImplementedError()

    def on_websocket_data(self, data):
        raise NotImplementedError()

    def on_channel_data(self, data):
        raise NotImplementedError()


    def run(self):
        websocket_fd = uwsgi.connection_fd()
        channel_fd = self.channel.connection._sock.fileno()

        fds = [websocket_fd, channel_fd]

        try:
            while True:
                readable, _, _ = select.select(fds, [], [], TIMEOUT)
                if not readable:
                    self.recv()
                    continue

                self.recv()
                data = self.channel.get_message(ignore_subscribe_messages=True)
                if data:
                    self.on_channel_data(data)

        except self.WebSocketError:
            return HttpResponse('ws ok')
        finally:
            self.channel.unsubscribe()
            self.on_connection_lost()

    @classonlymethod
    def as_view(cls):
        def wrapper(request, *args, **kwargs):
            self = cls(request, *args, **kwargs)
            return self.run()
        return wrapper

