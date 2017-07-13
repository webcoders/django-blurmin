from ui.adminpage import AdminPage
from django.conf import settings
from django.http import HttpResponseRedirect
import os
class HomeView(AdminPage):
    template_name = 'ui/index-dev.html' if hasattr(settings,'BLURMIN_DEVMODE') and settings.BLURMIN_DEVMODE else 'ui/index.html'

def ThemeRedirectView(request,arg):
    p = '/static/ui/' + request.path[len(settings.ADMIN_LOCATION)+1:]
    return HttpResponseRedirect(p)