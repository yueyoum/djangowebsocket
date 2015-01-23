from django.conf.urls import include, url
from django.contrib import admin

import apps.web.views
import apps.websocket.views


urlpatterns = [
    # Examples:
    # url(r'^$', 'example.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # url(r'^admin/', include(admin.site.urls)),

    url(r'^$', apps.web.views.Index.as_view()),
    url(r'^ws/$', apps.websocket.views.Chat.as_view()),
]
