import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.aggregates import Count
from django.http.response import HttpResponse

from ui.views.edit import FormView
from ui.views import BaseView
from django.utils.decorators import classonlymethod
from ui.views.gridview.filters.forms import EqualFilterForm, DateFilterForm, DateRangeFilterForm, \
    DateChoiceFilterForm, AutocompeleteEqualFilterForm
from django.core.urlresolvers import reverse
from ui import session
from ui import ui
from ui.models.utils import get_model_field_from_path


class FilterFormView(FormView, BaseView):
    template_name= 'ui/filters/filter.html'
    grid_queryset = None
    field_name = None

    @classonlymethod
    def urlpattern(cls):
        return r'^%s/%s/(?P<queryset>[a-z0-9]+)/(?P<field_name>[a-zA-Z_]+)$' % (
            str(cls.__module__), cls.__name__.lower())

    def get_form_kwargs(self):
        kwargs = super(FilterFormView, self).get_form_kwargs()
        self.field_name = self.kwargs['field_name']
        if self.kwargs['queryset']!='none':
            self.grid_queryset = session.load_queryset(self.request, self.kwargs['queryset'])
        return kwargs

    def get_prefix(self):
        return self.kwargs['field_name']


class EqualFilterFormView(FilterFormView):
    form_class = EqualFilterForm

    def get_form_kwargs(self):
        kwargs = super(EqualFilterFormView, self).get_form_kwargs()
        kwargs['choices'] = self.get_choices()
        kwargs['field'] = get_model_field_from_path(self.grid_queryset.model, self.field_name)
        if '__' in self.field_name:
            kwargs['field'].verbose_name = self.field_name.replace('__', ' ')
        kwargs['field'].verbose_name = kwargs['field'].verbose_name.title()
        return kwargs

    def get_queryset(self):
        self.grid_queryset.query.clear_ordering(force_empty=True)
        return self.grid_queryset.values(self.field_name).annotate(count=Count(self.field_name))

    def get_choices(self):
        return [(item, item) for item in self.get_queryset().values_list(self.field_name, flat=True)]


class AutocompleteEqualFilterFormView(EqualFilterFormView):
    form_class = AutocompeleteEqualFilterForm

    def get_form_kwargs(self):
        kwargs = super(AutocompleteEqualFilterFormView, self).get_form_kwargs()
        kwargs['url'] = reverse(self.__class__.__name__.lower(), kwargs=self.kwargs)
        return kwargs

    def get_queryset(self):
        if 'query' in self.request.GET:
            queryset = super(AutocompleteEqualFilterFormView, self).get_queryset()
            queryset.query.clear_ordering(force_empty=True)
            return queryset.filter(
                **{self.field_name + '__icontains': self.request.GET['query']})[:10]
        return super(AutocompleteEqualFilterFormView, self).get_queryset().none()

    def get_choices(self):
        return [(item, item) for item in self.get_queryset().values_list(self.field_name, flat=True)]

    def render_to_response(self, context, **response_kwargs):
        if 'json' in self.request.GET:
            return HttpResponse(
                json.dumps({'fields': [self.field_name], 'data': self.get_choices()}, cls=DjangoJSONEncoder))
        else:
            return super(AutocompleteEqualFilterFormView, self).render_to_response(context, **response_kwargs)


class DateFilterFormView(FilterFormView):
    form_class = DateFilterForm


class DateRangeFilterFormView(FilterFormView):
    form_class = DateRangeFilterForm


class DateChoiceFilterFormView(FilterFormView):
    form_class = DateChoiceFilterForm


ui.register(EqualFilterFormView)
ui.register(DateFilterFormView)
ui.register(DateRangeFilterFormView)
ui.register(DateChoiceFilterFormView)
ui.register(AutocompleteEqualFilterFormView)
