from django.shortcuts import render_to_response
from django.views.generic import View
from django.http import HttpResponseRedirect
from django import forms

class LoginForm(forms.Form):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'pure-input-1-1'}))


class Index(View):
    def get(self, request):
        name = request.session.get('name', None)
        if not name:
            return render_to_response(
                'login.html',
                {
                    'action': request.path,
                    'form': LoginForm().as_p()
                }
            )

        return render_to_response(
            'chat.html',
            {
                'websocket_url': 'ws://' + request.get_host()
            }
        )

    def post(self, request):
        form = LoginForm(request.POST)
        if not form.is_valid():
            return HttpResponseRedirect(request.path)

        name = form.cleaned_data['name']
        request.session['name'] = name
        return HttpResponseRedirect(request.path)
