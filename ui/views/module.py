from django.utils.decorators import classonlymethod
from django.utils.module_loading import import_string
from django.views.generic.base import TemplateView
from django.conf import settings

from ui.adminpage import AdminPage
from ui.views import BaseView


class DashboardMenuView(AdminPage):
    template_name= 'ui/dashboard/menu.html'
    menu = None

    def __init__(self, *args, **kwargs):
        self.menu = import_string(settings.ADMIN_MENU)
        return super(DashboardMenuView, self).__init__(*args, **kwargs)

    def get_menu_element(self, obj):
        elem = {
            'state': obj.__class__.__name__,
            'title': obj.title or obj.__class__.__name__,
            'icon': obj.icon,
            'abstract': str(obj.abstract).lower(),
        }
        if not obj.abstract:
            elem['url'] = obj.get_url()

        return elem

    def get_context_data(self, **kwargs):
        context = super(DashboardMenuView, self).get_context_data(**kwargs)
        _menu = []
        separate_modules = ''
        counter = 0
        for elem in self.menu:
            counter += 1
            elem = elem()
            if elem.in_menu(self.request.user):
                if elem.use_menu_template == 'module':
                    separate_modules += sub_elem.render_menu_module(context={'order': counter})
                    continue
                elif elem.use_menu_template == 'state':
                    _elem = {'body': elem.render_menu_module(context={'order': counter})}
                else:
                    _elem = self.get_menu_element(elem)
                _elem['items'] = []
                sub_counter = 0
                for sub_elem in elem._menu_items:
                    sub_counter += 1
                    sub_elem = sub_elem()
                    if sub_elem.in_menu(self.request.user):
                        if sub_elem.use_menu_template == 'module':
                            separate_modules += sub_elem.render_menu_module(parent=elem, context={'order': sub_counter})
                            continue
                        elif sub_elem.use_menu_template == 'state':
                            sub_elem = {'body':sub_elem.render_menu_module(parent=elem, context={'order': sub_counter})}
                        else:
                            sub_elem = self.get_menu_element(sub_elem)
                            sub_elem['state'] = '%s.%s' % (_elem['state'], sub_elem['state'])
                        _elem['items'].append(sub_elem)
                _menu.append(_elem)
        context['menu'] = _menu
        context['separate_modules'] = separate_modules
        return context

    @classonlymethod
    def urlpattern(cls):
        return r'^backend_module.js?$'
