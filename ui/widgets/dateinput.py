from django.forms import widgets
import re
from django.conf import settings
from django.utils import formats

DJANGOFORMATS__UIBDATEPARSER_MAP = {
    'Y': 'yyyy',  # 4 digits year.
    'y': 'yy',  # 2 digits year.
    'F': 'MMMM',  # full name of a month.
    'M': 'MMM',  # short name of a month.
    'N': 'MMM',  # short name of a month.
    'E': 'MMM',  # short name of a month.
    'n': 'MM',  # numeric month.
    'm': 'MM',  # numeric month.
    'd': 'dd',  # numeric day. Leading 0.
    'j': 'd',  # numeric day.
    'I': 'EEEE',  # full name of a day.
    'D': 'EEE',  # short name of a day.
    'H': 'HH',  # 24 hours time. Leading 0.
    'G': 'H',  # 24 hours time.
    'h': 'hh',  # 12 hours time. Leading 0.
    'g': 'h',  # 12 hours time.
    'i': 'mm',  # minutes. Leading 0.
    'u': 'sss',  # milliseconds.
    's': 'ss',  # seconds. Leading 0.
    'w': 'w',  # week number
}


def convert_format(django_format):
    results = re.findall(r'([a-zA-Z]+)', django_format)
    for r in results:
        django_format = django_format.replace(r, DJANGOFORMATS__UIBDATEPARSER_MAP[r])
    return django_format


class DateTimeInput(widgets.DateTimeInput):
    date_format = formats.get_format("SHORT_DATETIME_FORMAT",
                                     lang=settings.LANGUAGE_CODE)

    def render(self, name, value, attrs=None):
        js_format = convert_format(self.date_format)

        if 'ng-model' in self.attrs:
            self.attrs['ng-model'] = self.attrs['ng-model']
        self.attrs['datetime-picker'] = 'mediumDate'
        self.attrs['is-open'] = 'data.picker.open'
        self.attrs['datepicker-options'] = "data.picker.datepickerOptions"
        self.attrs['close-on-date-selection'] = "false"
        self.attrs['datepicker-append-to-body'] = "true"
        self.attrs['save-as'] = "true"
        self.attrs['read-as'] = "true"
        self.attrs['class'] = "form-control btn-group"
        self.attrs['datetime-picker'] = js_format
        return """
<div ng-controller="datepickerController as data" class="input-group datePicker" >
%(input)s
<span class="input-group-btn">
  <button type="button" class="btn btn-default" ng-click="data.openCalendar($event, 'picker')"><span class="glyphicon glyphicon-calendar"></span></i></button>
</span>
</div>

""" % {'name': name, 'value': value, 'input': super(DateTimeInput, self).render(name, value, attrs=attrs),
       'ng-model': self.attrs['ng-model']}


class DateInput(DateTimeInput):
    date_format = formats.get_format("DATE_FORMAT",
                                     lang=settings.LANGUAGE_CODE)

    def render(self, name, value, attrs=None):
        self.attrs['enable-time'] = "false";
        return super(DateInput, self).render(name, value, attrs=attrs)


class TimeInput(DateTimeInput):
    date_format = 'H:i'

    def render(self, name, value, attrs=None):
        self.attrs['enable-date'] = "false";
        return super(TimeInput, self).render(name, value, attrs=attrs)
