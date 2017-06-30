from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from ui.exceptions import HttpUnauthorized


class LoginRequiredMixin(LoginRequiredMixin):
    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        params = {'login_url': self.get_login_url(),
                  'full_path': self.request.get_full_path(),
                  'redirect_field_name': self.get_redirect_field_name()}
        response_401 = HttpUnauthorized(self.serialize(params))
        response_401.params = params
        return response_401


class PermissionRequiredMixin(PermissionRequiredMixin):
    def handle_no_permission(self):
        return HttpResponseForbidden('Forbidden')
