import functools
# import inspect
import os
from functools import update_wrapper

# from django.core.serializers import json
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseForbidden
from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe

from ui.adminpage import BaseAdminPageView, BaseAdminPage, MVS_TEMPLATE_DIR
from ui.forms.form import ModelForm
from ui.serializers.json_encoder import UiJSONEncoder
import json
from ui.views.gridview.view import GridView
from ui.views.edit import ChangeView, ng_get_model, DeleteView
from ui.exceptions import HttpUnauthorized
from django.conf import settings




class ViewSet(object):
    # [{'name':(pattern,cls),'name':(pattern,cls)}....]
    members = []
    base_url = None
    admin_page = None

    @classmethod
    def url_name(cls):
        # base = getattr(cls, 'base_url', False)
        return cls.base_url if cls.base_url else cls.__name__.lower()

    @classmethod
    def member_url_name(cls, name):
        return "%s_%s" % (cls.url_name(), name)

    @classmethod
    def get_member_url(cls, name):
        return reverse(cls.member_url_name(name))

    def get_menu_state_name(self):
        menu = import_string(settings.ADMIN_MENU)
        state = None
        my_page = self.__class__ if issubclass(self.__class__, AdminPageViewSet) else self.admin_page
        if my_page:
            for item in menu:
                if item == my_page:
                    # state = my_page.__name__
                    state = my_page.get_state_name()
                    return state
                for sub_item in item._menu_items:
                    if sub_item == my_page:
                        # state =  item.__name__ + '.' + my_page.__name__
                        state = item.get_state_name() + '.' + my_page.get_state_name()
                        return state;
        return state

    # def __init__(self,*args,**kwargs):
    #     super(ViewSet,self).__init__(*args,**kwargs)
    #     self.members = kwargs.get('members',self.members)
    def get_member_view(self, name):
        return getattr(self, name + '_view', self.members[name][1])

    def get_member_pattern(self, name):
        pattern = getattr(self, name + '_pattern', self.members[name][0])
        return '^/%s/$' % (pattern) if pattern else '^$'

    def get_urls(self):
        from django.conf.urls import url
        # def wrap(view):
        #     def wrapper(*args, **kwargs):
        #         return self.admin_site.admin_view(view)(*args, **kwargs)
        #     wrapper.model_admin = self
        #     return update_wrapper(wrapper, view)
        urlpatterns = []

        for name in self.members:
            urlpatterns. \
                append(
                url(self.get_member_pattern(name), self.get_member_view(name).as_view(**self.get_view_kwargs(name)),
                    name=self.member_url_name(name)))
        return urlpatterns

    def urls(self):
        return self.get_urls()

    urls = property(urls)

    def get_class_kwargs_names(self, cls):
        names = set(['model', 'template_name', 'row_id_field_name', 'queryset', 'show_notifications'])
        if issubclass(cls, GridView):
            names.symmetric_difference_update(set(['list_display', 'list_filter', 'list_order', 'list_editable',
                                                   'list_display_links', 'conditions', 'search_fields',
                                                   'paginate_per_page_list',
                                                   'allow_empty', 'queryset', 'paginate_by', 'paginate_orphans',
                                                   'paginator_class', 'context_object_name', 'paginator_class',
                                                   'ordering', 'page_kwarg', 'default_order', 'row_selector']))
        if issubclass(cls, ChangeView):
            names.symmetric_difference_update(
                set(['fields', 'readonly_fields', 'exclude', 'form_class', 'render_fields','content_reload_fields','render_form', 'render_fields_exclude']))
        if issubclass(cls, ViewSetMemberMixin):
            names.symmetric_difference_update(set(['separate_queryset']))
        if issubclass(cls, BaseAdminPageView):
            names.symmetric_difference_update(set(['title', 'panel_title', 'icon']))
        return list(names)

    def get_view_kwargs_attr(self, attr_name, name):
        """ check if viewset has attr with name prefixed with the member name first!
        for example 'list_model' will take precedence over  'model' for member with name='list'  """
        member_prefixed_attr_name = name + '_' + attr_name
        if hasattr(self, member_prefixed_attr_name):
            return getattr(self, member_prefixed_attr_name)
        return getattr(self, attr_name, False)

    def get_view_kwargs(self, name):
        initial_kwargs = {}
        if getattr(self, name + '_get_view_kwargs', None):
            initial_kwargs = getattr(self, name + '_get_view_kwargs')()
        else:
            cls = self.get_member_view(name)
            if not cls.standalone:
                kwargs_list = self.get_class_kwargs_names(cls)
                #             attributes = inspect.getmembers(self.__class__, lambda a: not (inspect.isroutine(a)))
                #             attributes = [a for a in attributes if a[0][:1] != '_' and a[0] not in ['members','urls']]
                for attr in kwargs_list:
                    value = self.get_view_kwargs_attr(attr, name)
                    if value:
                        initial_kwargs[attr] = value
        kwargs = {}
        # overwrite custom view properties,
        for attr in initial_kwargs:
            if hasattr(cls, attr) and initial_kwargs[attr]:
                kwargs[attr] = initial_kwargs[attr]

        kwargs['view_set'] = self
        kwargs['view_set_name'] = name
        return kwargs

    def rendered_content(self, request, name):
        func_result = self.get_member_view(name).as_view(**self.get_view_kwargs(name))(request)
        if isinstance(func_result, HttpUnauthorized):
            return "<script>window.location='%s?%s=/#%s'</script>" % (func_result.params['login_url'],
                                                                      func_result.params['redirect_field_name'],
                                                                      func_result.params['full_path'])
        if isinstance(func_result, HttpResponseForbidden):
            return "You don't have permissions."
        return func_result.render().content


class ViewSetMemberMixin(object):
    view_set = None
    view_set_name = None
    __template_name_postfix = ''
    standalone = False
    def _get_parent_method(self, name):
        parent_method = getattr(self.view_set, self.view_set_name + '_' + name, None)
        if not parent_method:
            parent_method = getattr(self.view_set, name, None)
        return parent_method

    def get_template_names(self):
        templates = []
        if self.template_name is not None:
            templates.append(self.template_name)
        templates.append(os.path.join(MVS_TEMPLATE_DIR, self.view_set.__class__.__name__,
                                      self.view_set_name + self.__template_name_postfix + '.html'))
        templates.append(os.path.join(MVS_TEMPLATE_DIR, self.view_set.url_name(),
                                      self.view_set_name + self.__template_name_postfix + '.html'))
        templates.append(os.path.join(MVS_TEMPLATE_DIR, self.view_set_name + self.__template_name_postfix + '.html'))
        templates.append(self.view_set_name + self.__template_name_postfix + '.html')
        return templates

    def url_name(self):
        return self.view_set.member_url_name(self.view_set_name)

    def get_url(self):
        return self.view_set.get_member_url(self.view_set_name)

    def get_context_data(self, **kwargs):
        ctx = super(ViewSetMemberMixin, self).get_context_data(**kwargs)
        ctx['view_name'] = self.url_name()
        ctx['view_url'] = self.get_url()
        return ctx


# TODO need to implement ViewSetMember.__call__ method to avoid need of redeclare method with callViewSet decorator
def callViewSet(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        parent_method = self._get_parent_method(func.__name__)
        if not parent_method or kwargs.get('_direct', False) or self.standalone:
            if kwargs.get('_direct', False):
                del kwargs['_direct']
            return func(self, *args, **kwargs)
        return parent_method(self, *args, **kwargs)

    return update_wrapper(wrapper, func)


class ViewSetMemberQuerySetMixin(object):
    separate_queryset = False

    def get_queryset(self):
        if not self.separate_queryset:
            self.queryset = self.view_set.get_queryset(self)
        return super(ViewSetMemberQuerySetMixin, self).get_queryset()


class GridViewSetMember(ViewSetMemberQuerySetMixin, ViewSetMemberMixin, GridView):
    list_editable = []
    template_name = None
    inline_change_view_member_name = 'change'

    def dispatch(self, request, *args, **kwargs):
        # save it for multiple usage in process_object
        if len(self.list_editable) > 0:
            self.inline_change_view_instance = self.view_set.get_member_view('change')(**self.view_set.get_view_kwargs('change'))
            self.inline_change_view_instance.request = request
            # self.form_class = self.view_set.get_changelist_form(request, *args, **kwargs)
        return super(GridViewSetMember, self).dispatch(request, *args, **kwargs)

    def get_changelist_form(self, request, object, *args, **kwargs):
        self.inline_change_view_instance.object = object
        form_class = self.inline_change_view_instance.get_form_class(fields=self.list_editable)
        form = self.inline_change_view_instance.get_form(form_class=form_class)
        return form

    @callViewSet
    def get_context_data(self, **kwargs):
        ctx = super(GridViewSetMember, self).get_context_data(**kwargs)
        ctx['list_editable'] = self.list_editable
        ctx['initial_data'] = json.dumps({'inline_form' : self.process_object({})}, cls=UiJSONEncoder)
        return ctx

    # def process_object(self, object):
    #     if not len(self.list_editable) > 0:
    #         return object
    #     object = super(GridViewSetMember, self).process_object(object)
    #     form = self.form_class(data=object, request=self.request)
    #     object['__inputs'] = {}
    #     object['__rowForm'] = ng_get_model(form, None, as_json=False)
    #     for field in self.list_editable:
    #         f = form.fields[field]
    #         f.widget.label = '';
    #         object['__inputs'][field] = mark_safe(f.widget.render(field, form.data[field], attrs=f.widget.attrs))
    #     return object

    def process_object(self,object):
        if not len(self.list_editable) > 0:
            return object
        object = super(GridViewSetMember,self).process_object(object)
        if object:
#TODO this is worse call, need to find a way to access results of gridview get_queryset
            obj = self.model.objects.get(**{self.row_id_field_name : object[self.row_id_field_name]})
            form = self.get_changelist_form(self.request, obj)
            # form = self.form_class(data=object,request=self.request)
        else:
            object = {}
            form = self.get_changelist_form(self.request, None)
            # form = self.form_class(request=self.request)
        object['__inputs']={}
        object['__rowForm']=ng_get_model(form,{},as_json=False)
        for field in self.list_editable:
            f = form.fields[field]
            f.widget.label = '';
            object['__inputs'][field] = mark_safe(f.get_bound_field(form, field).as_formgroup())
                #mark_safe(f.widget.render(field,(form.data[field] if field in form.data else form.data[field + '_id']),attrs=f.widget.attrs))
        return object



class ChangeViewSetMember(ViewSetMemberQuerySetMixin, ViewSetMemberMixin, ChangeView):
    template_name = None

    @callViewSet
    def get_fields(self):
        return super(ChangeViewSetMember, self).get_fields()

    @callViewSet
    def get_form_class(self, **kwargs):
        return super(ChangeViewSetMember, self).get_form_class(**kwargs)

    @callViewSet
    def get_form(self, form_class=None):
        return super(ChangeViewSetMember,self).get_form(form_class=form_class)

    @callViewSet
    def get_readonly_fields(self):
        return super(ChangeViewSetMember, self).get_readonly_fields()

    @callViewSet
    def get_content_reload_fields(self):
        return super(ChangeViewSetMember, self).get_content_reload_fields()

    @callViewSet
    def get_context_data(self, **kwargs):
        return super(ChangeViewSetMember, self).get_context_data(**kwargs)

    @callViewSet
    def get_ng_model(self,form, initial, readonly_fields=[], render_fields=[], as_json=True):
        return super(ChangeViewSetMember,self).get_ng_model(form, initial, readonly_fields=readonly_fields, render_fields=render_fields,
                            as_json=as_json)

    @callViewSet
    def get_object(self, queryset=None):
        return super(ChangeViewSetMember, self).get_object(queryset=queryset)

    @callViewSet
    def save_model(self, form, change):
        return super(ChangeViewSetMember, self).save_model(form,change)

class DeleteViewSetMember(ViewSetMemberQuerySetMixin, ViewSetMemberMixin, DeleteView):
    template_name = None
    @callViewSet
    def get_object(self, queryset=None):
        return super(DeleteViewSetMember, self).get_object(queryset=queryset)
    @callViewSet
    def delete(self, request, *args, **kwargs):
        return super(DeleteViewSetMember, self).delete(request,*args,**kwargs)


class ModelViewSet(ViewSet):
    """ Use view set member name prefix to direct attribute for specific member,
    for example: to pass template_name for 'list' member, attribute must have name: 'list_template_name' """
    members = {'list': ('', GridViewSetMember), 'change': ('change', ChangeViewSetMember),'delete': ('delete', DeleteViewSetMember)}
    model = None
    fields = None
    readonly_fields = []
    list_editable = []
    list_display = []
    list_display_links = ()
    exclude = []
    # add_form_template = None
    change_template_name = None
    list_template_name = None
    delete_confirmation_template = None
    delete_selected_confirmation_template = None
    object_history_template = None

    @classmethod
    def url_name(cls):
        url = getattr(cls, 'base_url', False)
        if not url and cls.model:
            url = cls.model._meta.model_name
        return url if url else  cls.__class__.__name__

    # def get_changelist_form(self, request, *args, **kwargs):
    #     instance = self.members['change'][1](**self.get_view_kwargs('change'))
    #     instance.request = request
    #     return instance.get_form_class(fields=self.list_editable)

    def get_fields(self, view):
        if view.request.GET.get('grid-row') and len(self.list_editable) > 0:
            return self.list_editable
        return view.get_fields(_direct=1)

    def get_readonly_fields(self, view):
        return view.get_readonly_fields(_direct=1);

    def get_form_class(self, view, **kwargs):
        return view.get_form_class(_direct=1, **kwargs)

    def get_queryset(self, view):
        return self.model.objects.all()

    def save_model(self, view, form, change):
        return view.save_model(form,change,_direct=1)

    def get_context_data(self, view, **kwargs):
        ctx = view.get_context_data(_direct=1, **kwargs)
        ctx['change_view_url'] = self.get_member_url('change')
        ctx['grid_view_name'] = self.member_url_name('list')
        ctx['state_name'] = self.get_menu_state_name()
        ctx['state_driven'] = "yes";
        return ctx


class BaseAdminPageViewSetMember(ViewSetMemberMixin, BaseAdminPageView):
    # It catches up mezanine 'base.html' because member name is 'base'
    # template_name = 'admin_page.html'
    @callViewSet
    def get_context_data(self, **kwargs):
        return super(BaseAdminPageViewSetMember, self).get_context_data(**kwargs)


class AdminPageViewSet(BaseAdminPage, ModelViewSet):
    members = {'base': ('', BaseAdminPageViewSetMember),
               'list': ('list', GridViewSetMember),
               'change': ('change', ChangeViewSetMember),
               'delete': ('delete', DeleteViewSetMember)}

    def get_context_data(self, view, **kwargs):
        context = super(AdminPageViewSet, self).get_context_data(view, **kwargs)
        context.update(view.get_context_data(_direct=1, **kwargs))
        if view.view_set_name == 'base':
            context['grid_view'] = self.rendered_content(view.request, 'list')
        return context

    @classmethod
    def get_url(cls):
        return cls.get_member_url('base')

    @classmethod
    def get_state_name(cls):
        state_name = cls.state_name
        if not state_name and cls.model:
            state_name = cls.model._meta.model_name
        return state_name if state_name else  cls.__class__.__name__

    @classmethod
    def get_state_url(cls):
        state_url = cls.state_url
        if not state_url and cls.model:
            state_url = cls.model._meta.model_name
        return state_url if state_url else  cls.__class__.__name__
