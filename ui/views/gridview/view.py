import functools
import inspect
from copy import copy
from functools import update_wrapper

from django.core.exceptions import FieldDoesNotExist
from django.db.models import QuerySet
from django.utils.decorators import classonlymethod
from django.utils.safestring import mark_safe
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView
from django import db

from ui.exceptions import HttpUnauthorized
from ui.views.edit import ng_get_model, DeleteView
from ui.views import BaseView
from ui.views.edit import ChangeView
from ui.views.gridview.filters.fields import FieldFilter
from django.core.paginator import EmptyPage
from django.http.response import HttpResponse, HttpResponseForbidden
from ui import session
from django.db import models
import operator
from django.conf import settings

class GridView(BaseView, ListView):
    template_name= 'ui/gridview.html'
    paginate_per_page_list = [10, 25, 50, 100]
    list_display_links = ['id']
    list_display = []
    list_filter = []
    list_order = ['*']
    conditions = []
    search_fields = []
    row_id_field_name = 'id'
    ordering = ('-pk',)
    row_selector = False
    _list_display_funcs = {}

    def get_list_display(self):
        return self.list_display

    def get_list_display_field_names(self, for_query=True):
        fields = []
        if self.get_list_display():
            for item in self.get_list_display():
                if type(item) in (tuple, list):
                    field = item[0]
                else:
                    field = item
                if type(field) == dict:
                    for key, value in field.items():
                        self._list_display_funcs[key] = value
                        if for_query:
                            for f in value:
                                fields.append(f)
                        else:
                            fields.append(key)
                        break
                else:
                    fields.append(field)
        else:
            fields = [field.name for field in self.model._meta.get_fields()]
        return fields

    def get_paginate_by(self, queryset):
        paginate_by = self.request.GET.get('perpage', self.paginate_by)
        if paginate_by:
            try:
                self.paginate_by = int(paginate_by)
            except ValueError:
                pass
        return super(GridView, self).get_paginate_by(queryset)

    def set_filter_queryset(self, queryset):
        self._queryset_key = session.save_queryset(self.request, queryset)

    def get_queryset(self):
        queryset = super(GridView, self).get_queryset()
        self.set_filter_queryset(queryset)
        for cond in self.conditions:
            queryset = queryset.filter(cond.get_expression())

        if 'search' in self.request.GET:
            search_string = self.request.GET['search']
            if search_string:
                queryset = self.get_search_results(queryset, search_string)

        if 'sort' in self.request.GET:
            sort = self.deserialize(self.request.GET['sort'])
            return queryset.order_by(*sort)
        return queryset
        # return queryset

    def filters_apply(self, request):
        self.conditions = []
        for filter_def in self.list_filter:
            if isinstance(filter_def, tuple):
                if type(filter_def[0]) != str and issubclass(filter_def[0], FieldFilter):
                    field = filter_def[1]
                    filter = filter_def[0](self, field)
                else:
                    filter = FieldFilter(self, filter_def[0])
                    field = filter_def[0]
            else:
                field = filter_def
                filter = FieldFilter(self, field)

            cond_name = request.GET.get(field + '-condition')
            if cond_name:
                for Condition in filter.get_conditions():
                    if Condition.name == cond_name:
                        cond = Condition(filter, request=self.request)
                        if cond.form:
                            if cond.form.is_valid():
                                self.conditions.append(cond)
                            else:
                                return HttpResponse(ng_get_model(cond.form, {}))

    def get(self, request, *args, **kwargs):
        self.filters_apply(request)
        return super(GridView, self).get(request, *args, **kwargs)

    def get_list_filter(self):
        return self.list_filter

    def get_search_fields(self):
        return self.search_fields

    def get_search_results(self, queryset, search_term):
        """
        Taken from Django Admin
        """

        # Apply keyword searches.
        def construct_search(field_name):
            if field_name.startswith('^'):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name

        search_fields = self.get_search_fields()
        if search_fields and search_term:
            orm_lookups = [construct_search(str(search_field))
                           for search_field in search_fields]
            for bit in search_term.split():
                or_queries = [models.Q(**{orm_lookup: bit})
                              for orm_lookup in orm_lookups]
                queryset = queryset.filter(reduce(operator.or_, or_queries))
        return queryset

    def pagination(self, page_obj):
        try:
            next_page_number = page_obj.next_page_number()
        except EmptyPage:
            next_page_number = None
        try:
            previous_page_number = page_obj.previous_page_number()
        except EmptyPage:
            previous_page_number = None

        ON_EACH_SIDE = 3
        ON_ENDS = 2
        DOT = '...'

        paginator, page_num = page_obj.paginator, page_obj.number - 1

        if paginator.num_pages <= 10:
            page_range = range(paginator.num_pages)
        else:
            # Insert "smart" pagination links, so that there are always ON_ENDS
            # links at either end of the list of pages, and there are always
            # ON_EACH_SIDE links at either end of the "current page" link.
            page_range = []
            if page_num > (ON_EACH_SIDE + ON_ENDS):
                page_range.extend(range(0, ON_ENDS))
                page_range.append(DOT)
                page_range.extend(range(page_num - ON_EACH_SIDE, page_num + 1))
            else:
                page_range.extend(range(0, page_num + 1))
            if page_num < (paginator.num_pages - ON_EACH_SIDE - ON_ENDS - 1):
                page_range.extend(range(page_num + 1, page_num + ON_EACH_SIDE + 1))
                page_range.append(DOT)
                page_range.extend(range(paginator.num_pages - ON_ENDS, paginator.num_pages))
            else:
                page_range.extend(range(page_num + 1, paginator.num_pages))

        return {
            'total_items': page_obj.paginator.count,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'next_page_number': next_page_number,
            'previous_page_number': previous_page_number,
            'page_size': self.paginate_by,
            'num_pages': page_obj.paginator.num_pages,
            'number': page_obj.number,
            'page_range': [str(i + 1) if i != DOT else i for i in page_range],
            'per_page_list': self.paginate_per_page_list,
        }

    def get_context_data(self, **kwargs):
        self.queryset = self.object_list
        if isinstance(self.queryset, QuerySet) and not self.queryset.ordered:
            self.object_list = super(ListView, self).get_queryset()
        context = super(GridView, self).get_context_data(**kwargs)
        self.list_display = self.get_list_display()
        db.reset_queries()
        list_filter = []
        for field in self.get_list_filter():
            if type(field) in (tuple, list):
                if type(field[0]) != str and issubclass(field[0], FieldFilter):
                    _filter = field[0](self, field[1])
                else:
                    _filter = FieldFilter(self, field[0])
                    _filter.verbose_name = field[1]
                if len(field) > 2:
                    _filter.verbose_name = field[2]
            else:
                _filter = FieldFilter(self, field)
            list_filter.append(_filter)

        queryset = context['object_list']

        if self.list_display:
            if type(queryset) in (list, tuple):
                context['object_list'] = queryset
            else:
                context['object_list'] = list(
                queryset.values(*(self.get_list_display_field_names() + [self.row_id_field_name])))
        else:
            context['object_list'] = list(queryset.values())

        field_labels = {}

        list_display = []

        if self.model:
            for field in self.model._meta.get_fields():
                if not self.list_display:
                    if hasattr(field, 'primary_key') and not field.primary_key:
                        list_display.append(field.name)
                if hasattr(field, 'verbose_name'):
                    field_labels[field.name] = field.verbose_name
        for item in self.list_display:
            if type(item) in (tuple, list):
                if type(item[0]) == dict:
                    for key in item[0].keys():
                        field_labels[key] = item[1]
                        break
                else:
                    field_labels[item[0]] = item[1]
            if '__' in item:
                field_labels[item] = item.replace('__', ' ').title()

        list_display_fields = self.get_list_display_field_names(for_query=False)

        context['list_display'] = list_display_fields
        if self.list_order == ['*']:
            context['list_order'] = list_display_fields
        else:
            context['list_order'] = self.list_order
        context['field_labels'] = field_labels
        context['url_name'] = self.url_name()
        context['list_display_links'] = self.list_display_links
        context['row_id_field_name'] = self.row_id_field_name
        context['row_selector'] = self.row_selector
        object_list = []

        for object in context['object_list']:
            for field in list_display_fields:
                if hasattr(self, field) and callable(getattr(self, field)):
                    func = getattr(self, field)
                    func_params = self._list_display_funcs[field]
                    if func_params == '*':
                        object[field] = getattr(self, field)(object)
                    object[field] = getattr(self, field)(*[object[param] for param in func_params])
#TODO make choice displaing work also for related fields!
                elif object[field] is not None:
                    try:
                        if hasattr(self.model, '_meta') and hasattr(self.model._meta.get_field(field), 'choices') \
                                and len(self.model._meta.get_field(field).choices)>0:
                            choice_vals = [v[0] for v in self.model._meta.get_field(field).choices]
                            try:
                                idx = choice_vals.index(object[field])
                                if idx:
                                    object[field] = self.model._meta.get_field(field).choices[idx][1]
                            except ValueError:
                                pass
                    except FieldDoesNotExist:
                        pass

            object_list.append(self.process_object(object))

        context['object_list'] = object_list

        if len(db.connection.queries) > 1 and not settings.DEBUG:
            raise ValueError('Too many queries to database. Class %s' %
                             self.__class__.__name__)

        if list_filter:
            context['list_filter'] = list_filter

        if self.request.is_ajax():
            return context

        if self.search_fields:
            context['search_fields'] = self.search_fields
        context['object_list'] = self.serialize(context['object_list'])
        context['view_name'] = self.__class__.__name__.lower()
        context['view_url'] = self.get_url()
        return context

    def get_json_context_data(self, context):
        result_context = {
            'view_name': self.__class__.__name__.lower(),
            'object_list': context['object_list']
        }
        if self.get_paginate_by(context['object_list']):
            result_context.update(self.pagination(context['page_obj']))
        _list_filter = []
        if 'list_filter' in context:
            for filter in context['list_filter']:
                conditions = []
                for Condition in filter.get_conditions():
                    condition = Condition(filter)
                    c = {'name': condition.name, 'ui': condition.get_url()}
                    if hasattr(condition, 'label'):
                        c['label'] = condition.label
                    conditions.append(c)
                _list_filter.append({'field': filter.field_name,
                                     'verbose_name': filter.verbose_name,
                                     'conditions': conditions})
        result_context.update({'list_filter': _list_filter})
        return result_context

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            return self.serialize(self.get_json_context_data(context))
        return super(GridView, self).render_to_response(context, **response_kwargs)

    def process_object(self,object):
        return object

class EditableGridView(GridView):
    template_name= 'ui/gridview-editable-inline.html'
    change_view_class = ChangeView
    change_view_template_name = "formview.html"
    change_view_fields = '__all__'
    change_view_form_class = None
    delete_view_class = DeleteView

    def get_change_view_kwargs(self):
        initial_kwargs = {'model': self.model, 'queryset': self.queryset,
                          'fields': self.change_view_fields if not self.change_view_form_class else None,
                          'template_name': self.change_view_template_name,
                          'form_class': self.change_view_form_class,
                          'parent_view': self}
        cls = self.get_change_view_class()
        kwargs = {}
        # prevent overwriting custom view properties, if we use other than ChangeView
        for attr in initial_kwargs:
            if not getattr(cls, attr) and initial_kwargs[attr]:
                kwargs[attr] = initial_kwargs[attr]
        return kwargs

    def get_change_view_class(self):
        return self.change_view_class

    def get_change_view(self):
        return self.get_change_view_class().as_view(**self.get_change_view_kwargs())

    def get_delete_view_kwargs(self):
        initial_kwargs = {'model': self.model, 'queryset': self.queryset,
                          'parent_view': self}
        cls = self.get_delete_view_class()
        kwargs = {}
        # prevent overwriting custom view properties, if we use other than ChangeView
        for attr in initial_kwargs:
            if not getattr(cls, attr) and initial_kwargs[attr]:
                kwargs[attr] = initial_kwargs[attr]
        return kwargs

    def get_delete_view_class(self):
        return self.delete_view_class

    def get_delete_view(self):
        return self.get_delete_view_class().as_view(**self.get_delete_view_kwargs())

    def get(self, request, *args, **kwargs):
        last_el = request.path.split('/')[-2] if request.path[-1] == '/' else request.path.split('/')[-1]
        if last_el == 'change':
            return self.get_change_view()(request)
        elif last_el == 'delete':
            return self.get_delete_view()(request)
        return super(EditableGridView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.get_change_view()(request)

    def get_context_data(self, **kwargs):
        ctx = super(EditableGridView, self).get_context_data(**kwargs)
        ctx['change_view_url'] = self.get_url() + '/change/'
        ctx['delete_view_url'] = self.get_url() + '/delete/'
        if ctx.get('view_name',False):
            ctx['grid_view_name'] = ctx['view_name']
        return ctx

    def on_dispatch(self,request, *args, **kwargs):
        self.change_view_instance = self.change_view_class(**self.get_change_view_kwargs())
        self.change_view_instance.request = request
        self.delete_view_instance = self.delete_view_class(**self.get_delete_view_kwargs())
        self.delete_view_instance.request = request

    def dispatch(self, request, *args, **kwargs):
        self.on_dispatch(request, *args, **kwargs)
        return super(EditableGridView,self).dispatch(request, *args, **kwargs)


from ui.serializers.json_encoder import UiJSONEncoder
import json

class InlineEditableGridView(EditableGridView):
    template_name= 'ui/gridview-editable-inline.html'
    list_editable = []
#TODO Do something with changeview integration more clear way!
    def  __init__(self,*args,**kwargs):
        super(InlineEditableGridView,self).__init__(*args,**kwargs)
    def on_dispatch(self,request, *args, **kwargs):
        super(InlineEditableGridView, self).on_dispatch(request, *args, **kwargs)
        if not len(self.list_editable):
           return
        self.change_view_instance.fields = self.list_editable
        self.change_view_instance_form_class = self.change_view_instance.get_form_class()
    def get_context_data(self, **kwargs):
        ctx = super(EditableGridView, self).get_context_data(**kwargs)
        ctx['list_editable'] = self.list_editable
        ctx['initial_data'] = json.dumps({'inline_form' : self.process_object({})}, cls=UiJSONEncoder)
        return ctx
    def process_object(self,object):
        object = super(InlineEditableGridView,self).process_object(object)
        if object:
            form = self.change_view_instance_form_class(data=object,request=self.request)
        else:
            object = {}
            form = self.change_view_instance_form_class(request=self.request)
        object['__inputs']={}
        object['__rowForm']=ng_get_model(form,{},as_json=False)
        for field in self.list_editable:
            f = form.fields[field]
            f.widget.label = ''
            f.widget.attrs['label_position'] = 'horizontal'
            object['__inputs'][field] = mark_safe(f.get_bound_field(form, field).as_formgroup())
                #mark_safe(f.widget.render(field,(form.data[field] if field in form.data else form.data[field + '_id']),attrs=f.widget.attrs))
        return object
