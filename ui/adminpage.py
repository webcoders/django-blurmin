import os

from django.http.response import HttpResponseRedirect
from django.template.response import SimpleTemplateResponse
from django.views.generic.base import TemplateView
from ui.views import BaseView
from django.conf import settings

MVS_TEMPLATE_DIR = 'ui/mvs'

class BaseAdminPage(object):
    title = ''
    panel_title = ''
    abstract = False
    hidden = False
    mvs = None
    # (can be 'module' or 'state' or template_name)
    use_menu_template = False
    icon = ''
    _menu_items = []
    state_name = ''
    state_url = ''

    def in_menu(self, user):
        return True

    def get_context_data(self, *args, **kwargs):
        context = super(BaseAdminPage, self).get_context_data(*args, **kwargs)
        context.update({'title': self.title,
                        'icon': self.icon,
                        'panel_title': self.panel_title})
        return context

    @classmethod
    def menu_items(cls, *args):
        cls._menu_items = list(args)
        return cls

    @classmethod
    def get_state_name(cls):
        return cls.state_name if cls.state_name else  cls.__name__

    @classmethod
    def get_state_url(cls):
        return cls.state_url if cls.state_url else  cls.__name__

    @classmethod
    def menu_module_template_names(cls):
        from ui.views.viewset import ViewSet
        res = []
        postfix = '_state.html'
        if cls.use_menu_template == 'module':
            postfix = '_module.js'
        elif cls.use_menu_template != 'state':
            res.append(cls.use_menu_template)

        if cls.mvs or issubclass(cls, ViewSet):
            res = res + [os.path.join(MVS_TEMPLATE_DIR,cls.__name__,'menu' + postfix)   , MVS_TEMPLATE_DIR+'/menu' + postfix]
            return res
        return res + [cls.__name__ + postfix, 'menu' + postfix]


    def render_menu_module(self, parent=None, context={}):
        from ui.views.viewset import AdminPageViewSet
        mvs = self.mvs() if self.mvs else (self if (isinstance(self,AdminPageViewSet)) else None)
        if mvs:
            context['mvs'] = mvs
            context['parent_state'] = parent.__class__.__name__ + '.' if parent else ''
            context.update({'state_name': self.get_state_name(),
                            'state_url': self.get_state_url(),
                            'title': self.title or self.__class__.__name__,
                            'icon': self.icon,
                            'hidden': self.hidden,
                            'url': self.get_url(),
                            'change_url': mvs.get_member_url('change'),
                            'row_id_field_name': (
                            mvs.row_id_field_name if getattr(mvs, 'row_id_field_name', False) else 'id')
                            })
        else:
            context.update({'state_name': self.state_name,
                            'state_url': self.state_url,
                            'title': self.title or self.__class__.__name__,
                            'icon': self.icon,
                            'hidden': self.hidden,
                            'url': self.get_url(),
                            'row_id_field_name': (self.row_id_field_name)
                            })
        res = SimpleTemplateResponse(self.menu_module_template_names(), context).rendered_content
        return res

class BaseAdminPageView(TemplateView, BaseView):
    template_name= 'ui/page.html'
    title = ''
    panel_title = ''
    icon = ''
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated() and not request.is_ajax():
            return HttpResponseRedirect(settings.LOGIN_URL)
        return super(BaseAdminPageView, self).get(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super(BaseAdminPageView, self).get_context_data(**kwargs)
        context.update({'title': self.title,
                        'icon': self.icon,
                        'settings': settings,
                        'panel_title': self.panel_title})
        return context


class AdminPage(BaseAdminPage, BaseAdminPageView):
    pass
