import operator
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http.response import HttpResponse
from django.utils.decorators import classonlymethod
from django.views.generic.base import View
from django.apps import apps
from ui import ui
from ui.views import BaseView
import json
from ui import session

class AutocompleteView(BaseView, View):

    rows_count = 10
    queryset = None
    search_fields = []
    display_fields = []
    search_string = ''
    extra_params = None
    extra_params_values = None

    id_field = 'pk'

    def __init__(self, request=None, queryset=None, search_fields=None, display_fields=None, extra_params=None, *args, **kwargs):
        if request:
            self.request = request
        self.queryset = queryset
        self.search_fields = search_fields
        self.display_fields = display_fields
        self.extra_params = extra_params
        super(AutocompleteView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        queryset = self.queryset
        if self.extra_params_values:
           # q_extra = self.get_extra_filter()
           queryset = queryset.filter(self.get_extra_filter())
        if self.search_string:
            q = []
            for field in self.search_fields:
                q.append(Q(**{field + '__istartswith': self.search_string}))
            queryset = queryset.filter(reduce(operator.or_, q))
        return queryset

    def get_extra_filter(self):
        q = []
        for field in self.extra_params_values:
            q.append(Q(**{field :self.extra_params_values[field]}))
        return reduce(operator.and_, q)

    def get_fields(self):
        fields = self.display_fields
        if not fields:
            fields = self.search_fields
        if self.id_field not in fields or fields[0] != self.id_field:
            fields = [self.id_field] + fields
        return fields

    def get_data(self):
        values = list(self.get_queryset().values_list(*self.get_fields())[:self.rows_count])
        data = {'fields': self.get_fields(), 'data': values}
        return data

    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '')
        self.queryset = session.load_queryset(self.request, kwargs['queryset'])
        self.search_fields = kwargs['search_fields'].split(',')
        self.display_fields = kwargs['display_fields'].split(',')
        self.extra_params = kwargs['extra_params'].split(',')
        self.search_string = query
        if self.extra_params:
            for arg in self.extra_params:
                if request.GET.get(arg, None):
                    if self.extra_params_values is None:
                        self.extra_params_values = {}
                    self.extra_params_values[arg] = request.GET[arg]

        return HttpResponse(self.serialize(self.get_data()))

    @classonlymethod
    def urlpattern(cls):
        return r'^%s/%s/(?P<queryset>[a-zA-Z0-9]+)/(?P<search_fields>[a-zA-Z_,]+)/(?P<display_fields>[a-zA-Z_,]+)/(?P<extra_params>[a-zA-Z_,]+)$' % (
            str(cls.__module__), cls.__name__.lower())

    def get_url(self):
        self._queryset_key = session.save_queryset(self.request, self.queryset)
        return reverse(self.url_name(), kwargs={'queryset': self._queryset_key,
                                                'search_fields': ','.join(self.search_fields),
                                                'display_fields': ','.join(self.display_fields or self.search_fields),
                                                'extra_params': ','.join(self.extra_params) if self.extra_params else '__none__' }
                       )


ui.register(AutocompleteView)
