# coding: utf-8
from django.core.exceptions import FieldDoesNotExist
from django.db.models.constants import LOOKUP_SEP

from ui.models.utils import get_model_field_from_path
from ui.views.gridview.filters.conditions import EqualCondition, TodayCondition, ThisWeekCondition, \
    ThisMonthCondition, ThisYearCondition, ChoiceDateCondition, DateRangeCondition, AutocompleteEqualCondition


class FieldFilter(object):
    conditions = [EqualCondition, ]
    verbose_name = None

    def get_conditions(self):
        return self.conditions

    def __init__(self, datagrid, field_name):
        self.datagrid = datagrid
        self.field_name = field_name
        if self.datagrid.model:
            self.model_field = get_model_field_from_path(self.datagrid.model, field_name)
            if not self.verbose_name:
                if hasattr(self.model_field, 'verbose_name'):
                    self.verbose_name = unicode(self.model_field.verbose_name)
            if not self.verbose_name:
                self.verbose_name = field_name
            if '__' in field_name:
                self.verbose_name = field_name.replace('__', ' ')
            self.verbose_name = self.verbose_name.title()


class DateFieldFilter(FieldFilter):
    conditions = [TodayCondition, ThisWeekCondition, ThisMonthCondition, ThisYearCondition,
                  ChoiceDateCondition, DateRangeCondition]

class AutocompleteFieldFilter(FieldFilter):
    conditions = [AutocompleteEqualCondition]