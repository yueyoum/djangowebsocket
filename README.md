# DjangoWebsocket

在Django中使用Websocket

需要 

*   uwsgi
*   gevent
*   redis


#### 完善中...


## Usage


#### wsgi

在项目目录中创建一个 `wsgi_websocket.py` 文件， 建议与 django自己的 `wsgi.py` 放在相同目录下

内容如下：

```python
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")

from djangowebsocket.wsgi import get_wsgi_application
application = get_wsgi_application()

```

#### view

view要继承 `djangowebsocket.view.WebSocketView` 

并且实现四个方法

例子：

```python

from djangowebsocket.view import WebSocketView

class MyView(WebSocketView):
    def on_connect(self):
        # 客户端链接上来会调用的函数
        # 在这里做一些初始化工作
        #
        # 属性：
        # self.request       django WSGIRequest
        # self.redis         redis client
        # self.channel       redis pubsub endpiont
        #
        # 方法：
        # self.send(text)               向客户端发送text数据
        # self.send_binary(binary)      向客户端发送binary数据
        # self.publish_global(text)     向所有链接的客户端广播数据

    def on_websocket_data(self, data):
        # 从client接收到的数据

    def on_channel_data(self, data):
        # 从 redis pubsub 中获取的数据

    def on_connection_lost(self):
        # 客户端断开链接

```

#### urls

将 你的url 映射到  `myapp.views.MyView.as_view()`


## Example
example 是一个聊天例子， 在这里可以测试： http://114.215.129.77:8111



## 注意

uwsgi 跑在 gevent 的事件循环上，每个客户端链接跑在一个greenlet中，
所以当链接的客户端数量 大于 uwsgi 配置中的 processes * gevent 总数，新客户端就不能链接










