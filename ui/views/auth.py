from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponseForbidden
from django.template.response import TemplateResponse
from django.views.generic.base import TemplateView
from ui.exceptions import HttpUnauthorized
from ui.views import BaseView
from django.contrib.auth.forms import AuthenticationForm
from django.utils.http import is_safe_url
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login
from django.conf import settings
from django.shortcuts import resolve_url
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
# from mezzanine.utils.views import set_cookie
# from mauth.views.accounts import login_get_redirect

class LoginView(TemplateView, BaseView):
    template_name= 'ui/auth/login.html'

    def get(self, request, *args, **kwargs):
        if 'logout' in request.GET:
            logout(request)
            HttpResponseRedirect(self.get_url())
        return super(LoginView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        redirect_to = self.request.GET.get(REDIRECT_FIELD_NAME, '')
        context = {
            REDIRECT_FIELD_NAME: redirect_to
        }
        return context

    def post(self, request, *args, **kwargs):
        redirect_to = request.POST.get(REDIRECT_FIELD_NAME, '')
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())
            acc_type = ''
            # acc_type,redirect = login_get_redirect(request)
            # if redirect:
            #     return redirect
            # else:
            return HttpResponseRedirect(redirect_to)
        context = {
            'form': form,
            REDIRECT_FIELD_NAME: redirect_to
        }
        return TemplateResponse(request, self.template_name, context)


