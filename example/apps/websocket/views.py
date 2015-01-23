#! -*- coding: utf-8 -*-


import datetime

from djangowebsocket.view import WebSocketView

now = lambda : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def log(text):
    print "{0}: {1}".format(now(), text)


class Chat(WebSocketView):
    def on_connect(self):
        print "on connect"

        self.name = self.request.session['name']
        client_amount = self.redis.incr('demo-client-amount')
        self.send(u"{0} {1} 人在线".format(now(), client_amount).encode('utf-8'))
        self.publish_global(u"{0} {1} 上线了".format(now(), self.name).encode('utf-8'))

    def on_websocket_data(self, data):
        print "websocket data:", data
        self.publish_global(u"{0} {1}: {2}".format(now(), self.name, data).encode('utf-8'))

    def on_channel_data(self, data):
        print "channel data", data
        data = str(data['data'])
        self.send(data)

    def on_connection_lost(self):
        print "connection lost"
        self.redis.incr('demo-client-amount', -1)
        self.publish_global(u"{0} {1} 下线了".format(now(), self.name).encode('utf-8'))
