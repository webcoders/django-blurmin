from django.urls.exceptions import NoReverseMatch

from django.utils.decorators import classonlymethod
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.core.urlresolvers import reverse
from ui.adminpage import BaseAdminPage
from ui.views import BaseView
from ui.views.edit import ChangeView, DeleteView
from ui import session
from ui.views.gridview.view import EditableGridView, InlineEditableGridView


class AdminPage(BaseAdminPage, BaseView, TemplateView):
    pass

class ChangeViewMixin(object):
    def get_change_view_kwargs(self):
        kwargs = super(ChangeViewMixin, self).get_change_view_kwargs()
        kwargs['_queriset_session_id'] = session.save_queryset(self.request, self.get_queryset())
        return kwargs
    def get_context_data(self, **kwargs):
        ctx = super(ChangeViewMixin, self).get_context_data(**kwargs)
        try:
            if self.change_view_instance:
                ctx['change_view_url'] = self.change_view_instance.get_url()
        except NoReverseMatch:
            pass
        return ctx

class DeleteViewMixin(object):
    def get_delete_view_kwargs(self):
        kwargs = super(DeleteViewMixin, self).get_delete_view_kwargs()
        kwargs['_queriset_session_id'] = session.save_queryset(self.request, self.get_queryset())
        return kwargs
    def get_context_data(self, **kwargs):
        ctx = super(DeleteViewMixin, self).get_context_data(**kwargs)
        try:
            if self.delete_view_instance:
                ctx['delete_view_url'] = self.delete_view_instance.get_url()
        except NoReverseMatch:
            pass
        return ctx

class EditableGridView(ChangeViewMixin,DeleteViewMixin,EditableGridView):
    pass
    # def get_change_view_kwargs(self):
    #     kwargs = super(EditableGridView, self).get_change_view_kwargs()
    #     kwargs['_queriset_session_id'] = session.save_queryset(self.request, self.get_queryset())
    #     return kwargs
    # # def get_delete_view_kwargs(self):
    #     kwargs = super(EditableGridView, self).get_delete_view_kwargs()
    #     kwargs['_queriset_session_id'] = session.save_queryset(self.request, self.get_queryset())
    #     return kwargs
    # def get_context_data(self, **kwargs):
    #     ctx = super(EditableGridView, self).get_context_data(**kwargs)
    #     try:
    #         if self.change_view_instance:
    #             ctx['change_view_url'] = self.change_view_instance.get_url()
    #         if self.delete_view_instance:
    #             ctx['delete_view_url'] = self.delete_view_instance.get_url()
    #     except NoReverseMatch:
    #         pass
    #     return ctx

class InlineEditableGridView(ChangeViewMixin,DeleteViewMixin,InlineEditableGridView):
    pass
    # def get_change_view_kwargs(self):
    #     kwargs = super(InlineEditableGridView, self).get_change_view_kwargs()
    #     kwargs['_queriset_session_id'] = session.save_queryset(self.request, self.get_queryset())
    #     return kwargs
    # def get_delete_view_kwargs(self):
    #     kwargs = super(InlineEditableGridView, self).get_delete_view_kwargs()
    #     kwargs['_queriset_session_id'] = session.save_queryset(self.request, self.get_queryset())
    #     return kwargs
    # def get_context_data(self, **kwargs):
    #     ctx = super(InlineEditableGridView, self).get_context_data(**kwargs)
    #     try:
    #         if self.change_view_instance:
    #             ctx['change_view_url'] = self.change_view_instance.get_url()
    #         if self.delete_view_instance:
    #             ctx['delete_view_url'] = self.delete_view_instance.get_url()
    #     except NoReverseMatch:
    #         pass
    #     return ctx

class ChangeView(DeleteViewMixin, ChangeView, BaseView):

    _queriset_session_id = None

    def __init__(self, *args, **kwargs):
        return super(ChangeView, self).__init__(*args, **kwargs)

    @classonlymethod
    def urlpattern(cls):
        return r'^%s/(?P<queryset>[a-zA-Z0-9]+)/((change/?)|(create/?))?$' % (cls.__name__.lower())

    def get_url(self):
        return reverse(self.url_name(), kwargs={'queryset': self._queriset_session_id})

    def dispatch(self, request, *args, **kwargs):
        if 'queryset' in kwargs:
            self._queriset_session_id = kwargs['queryset']
        return super(ChangeView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return session.load_queryset(self.request, self._queriset_session_id)

    # def get_delete_view_kwargs(self):
    #     kwargs = super(ChangeView, self).get_delete_view_kwargs()
    #     kwargs['_queriset_session_id'] = session.save_queryset(self.request, self.get_queryset())
    #     return kwargs
    #
    # def get_context_data(self, **kwargs):
    #     ctx = super(ChangeView,self).get_context_data(**kwargs)
    #     try:
    #         if self.delete_view_instance:
    #             ctx['delete_view_url'] = self.delete_view_instance.get_url()
    #     except NoReverseMatch:
    #         pass
    #     return ctx

class DeleteView(DeleteView, BaseView):
    _queriset_session_id = None

    def __init__(self, *args, **kwargs):
        return super(DeleteView, self).__init__(*args, **kwargs)

    @classonlymethod
    def urlpattern(cls):
        return r'^%s/(?P<queryset>[a-zA-Z0-9]+)/delete/$' % (cls.__name__.lower())

    def get_url(self):
        return reverse(self.url_name(), kwargs={'queryset': self._queriset_session_id})

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        if 'queryset' in kwargs:
            self._queriset_session_id = kwargs['queryset']
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return session.load_queryset(self.request, self._queriset_session_id)

