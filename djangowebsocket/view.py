# -*- coding: utf-8 -*-

__author__ = 'Wang Chao'
__date__ = '15-1-9'

import uwsgi
from gevent import select

from django.http import HttpResponse
from django.utils.decorators import classonlymethod


class WebSocketView(object):
    TIMEOUT = 10

    class WebSocketError(Exception):
        pass

    def recv(self):
        try:
            data = uwsgi.websocket_recv_nb()
            if data:
                self.on_websocket_data(data)
        except:
            # print "==== Error ===="
            # import traceback
            # traceback.print_exc()
            self.on_connection_lost()
            raise self.WebSocketError()

    def send(self, text):
        uwsgi.websocket_send(text)

    def send_binary(self, binary_data):
        uwsgi.websocket_send_binary(binary_data)

    def on_connection_lost(self):
        raise NotImplementedError()

    def on_websocket_data(self, data):
        raise NotImplementedError()

    def on_channel_data(self, data):
        raise NotImplementedError()

    def subcribe_channel(self):
        raise NotImplementedError()

    def initialize(self, request):
        raise NotImplementedError()

    def finish(self, request):
        raise NotImplementedError()


    def run(self, request):
        self.initialize(request)

        websocket_fd = uwsgi.connection_fd()

        channel = self.subcribe_channel()
        channel_fd = channel.connection._sock.fileno()

        fds = [websocket_fd, channel_fd]

        try:
            while True:
                readable, _, _ = select.select(fds, [], [], self.TIMEOUT)
                if not readable:
                    self.recv()
                    continue

                for rfd in readable:
                    if rfd == websocket_fd:
                        self.recv()
                    if rfd == channel_fd:
                        data = channel.get_message()
                        if data:
                            self.on_channel_data(data)
        except:
            self.finish(request)

        return HttpResponse()


    @classonlymethod
    def as_view(cls):
        self = cls()
        return self.run

