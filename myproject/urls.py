"""djangui URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from ui.register import *
from ui.notifications import uiadmin
from myapp import blurmin
from ui.views.home import HomeView,ThemeRedirectView
from django.conf import settings

urlpatterns = [
url(r'^admin/', admin.site.urls),
url(r'^%s' % settings.ADMIN_LOCATION, include([
    url(r'^$', HomeView.as_view()),
# This needed only for running without nginx!!! We recommend to use nginx rewrites you can found under /deploy
    url('^(app|assets|fonts|img|lib|sass)/',ThemeRedirectView),
    url(r'^ui/', ui.urls),
    # url(r'^send_notifications/$', notification_view),
    ]))
]
