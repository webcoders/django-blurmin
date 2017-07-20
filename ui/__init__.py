__version__ = '0.1a1'

from django.conf.urls import url,include

from ui.exceptions import AlreadyRegistered


class UI(object):
    _registry = []
    _viewset=[]
    __registered_patterns = []

    def get_urls(self):
        from ui.views.viewset import ViewSet
        from ui.views import BaseView
        urlpatterns = []
        for class_view in self._registry:
            if issubclass(class_view,ViewSet):
                vs = class_view()
                self._viewset.append(vs)
                urlpatterns += [
                    url(vs.url_name(),
                        include(vs.urls)),
                ]
            else:
                if not hasattr(class_view, 'urlpattern'):
                    continue
                pattern = class_view.urlpattern()
                if pattern in self.__registered_patterns:
                    raise AlreadyRegistered('%s' % pattern)
                urlpatterns += [
                    url(pattern,
                        class_view.as_view(),
                        name=class_view.url_name()),
                ]
            self.__registered_patterns.append(pattern)
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), None, None

    def register(self, class_view):
        # if not issubclass(class_view, View):
        #     raise ValueError('Need descendant of View class')
        if not class_view in self._registry:
            self._registry.append(class_view)


ui = UI()
