# -*- coding: utf-8 -*-

__author__ = 'Wang Chao'
__date__ = '15-1-9'

import uwsgi

import django
from django.conf import settings
from django.core import urlresolvers
from django.core.handlers.wsgi import WSGIHandler


class WebSocketApplication(WSGIHandler):
    def get_response(self, request):
        uwsgi.websocket_handshake()

        urlconf = settings.ROOT_URLCONF
        urlresolvers.set_urlconf(urlconf)
        resolver = urlresolvers.RegexURLResolver(r'^/', urlconf)

        response = None
        # Apply request middleware
        for middleware_method in self._request_middleware:
            response = middleware_method(request)
            if response:
                return response

        if hasattr(request, 'urlconf'):
            # Reset url resolver with a custom urlconf.
            urlconf = request.urlconf
            urlresolvers.set_urlconf(urlconf)
            resolver = urlresolvers.RegexURLResolver(r'^/', urlconf)

        resolver_match = resolver.resolve(request.path_info)
        callback, callback_args, callback_kwargs = resolver_match
        request.resolver_match = resolver_match

        # Apply view middleware
        for middleware_method in self._view_middleware:
            response = middleware_method(request, callback, callback_args, callback_kwargs)
            if response:
                return response

        wrapped_callback = self.make_view_atomic(callback)
        try:
            response = wrapped_callback(request, *callback_args, **callback_kwargs)
        except Exception as e:
            # If the view raised an exception, run it through exception
            # middleware, and if the exception middleware returns a
            # response, use that. Otherwise, reraise the exception.
            for middleware_method in self._exception_middleware:
                response = middleware_method(request, e)
                if response:
                    return response

                raise e

        return response


def get_wsgi_application():
    django.setup()
    return WebSocketApplication()

application = get_wsgi_application()


