import datetime

from django.db.models.constants import LOOKUP_SEP
from django.db.models.query_utils import Q

from ui.forms import add_prefix
from ui.views.gridview.filters.form_views import EqualFilterFormView, DateFilterFormView, DateRangeFilterFormView, \
    DateChoiceFilterFormView, AutocompleteEqualFilterFormView
from django.core.urlresolvers import reverse
from django import forms


class Condition(object):
    name = 'Filter'
    template_name = None
    field = None
    form_view = None
    values = None
    form = None

    def __init__(self, filter, request=None):
        self.filter = filter
        if request:
            self.request = request
            self.form = self.validate_form()

    def get_url(self):
        queryset_key = 'none'
        if hasattr(self.filter.datagrid, '_queryset_key'):
            queryset_key = self.filter.datagrid._queryset_key
        return reverse(self.form_view.__name__.lower(), kwargs={'queryset': queryset_key,
                                              'field_name': self.filter.field_name})

    def validate_form(self):
        form = self.get_form()
        if not form:
            return None
        if form.is_valid():
            self.values = form.cleaned_data
        return form

    def get_form_kwargs(self):
        form_class = self.form_view.form_class
        kwargs = {'prefix': self.filter.field_name}
        # kwargs ={}
        data = {}
        for field in form_class.base_fields:
            prefixed = add_prefix(self.filter.field_name, field)
            data[prefixed] = self.request.GET.get(prefixed)
            if not data[prefixed]:
                return None
        if self.request.GET.get('csrfmiddlewaretoken'):
            data['csrfmiddlewaretoken'] = self.request.GET.get('csrfmiddlewaretoken')
        kwargs['data'] = data
        return kwargs

    def get_form(self):
        kwargs = self.get_form_kwargs()
        if not kwargs:
            return None
        form_class = self.form_view.form_class
        return form_class(**kwargs)

    def get_expression(self):
        q = {}
        if self.values:
            for value in self.values:
                q[self.filter.field_name] = self.values[value]
            return Q(**q)
        else:
            return Q()


class AutocompleteEqualCondition(Condition):
    name = '_Equal'
    label = 'Equal'
    form_view = AutocompleteEqualFilterFormView


class EqualCondition(Condition):
    name = 'Equal'
    form_view = EqualFilterFormView


class ThisYearCondition(Condition):
    name = 'This Year'
    form_view = DateFilterFormView

    def get_expression(self):
        return Q(**{self.filter.field_name + '__year': datetime.date.today().year})


class ThisMonthCondition(Condition):
    name = 'This Month'
    form_view = DateFilterFormView

    def get_expression(self):
        return Q(**{self.filter.field_name + '__month': datetime.date.today().month,
                    self.filter.field_name + '__year': datetime.date.today().year})


class ThisWeekCondition(Condition):
    name = 'This Week'
    form_view = DateFilterFormView

    def get_expression(self):
        dow = datetime.date.today().weekday()
        return Q(**{self.filter.field_name + '__gte': datetime.date.today() - datetime.timedelta(dow),
                    self.filter.field_name + '__lte': datetime.date.today() + datetime.timedelta(6 - dow)})


class TodayCondition(Condition):
    name = 'Today'
    form_view = DateFilterFormView

    def get_expression(self):
        return Q(**{self.filter.field_name: datetime.date.today()})


class DateRangeCondition(Condition):
    name = 'Date Range'
    form_view = DateRangeFilterFormView

    def get_expression(self):
        return Q(
            **{self.filter.field_name + '__gte': self.values['date_from'], self.filter.field_name + '__lte': self.values['date_to']})


class ChoiceDateCondition(Condition):
    name = 'Choice Date'
    form_view = DateChoiceFilterFormView

    def get_expression(self):
        return Q(**{self.filter.field_name: self.values['date']})
