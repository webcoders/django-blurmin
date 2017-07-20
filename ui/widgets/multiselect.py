import json

from django.forms import widgets
from django.forms.widgets import SelectMultiple
from django.template.loader import render_to_string

from ui.widgets.autocomplete import Autocomplete


class MultiSelect(Autocomplete, SelectMultiple):


    def render(self, name, value, attrs=None):
        input_attrs = {}
        input_attrs['ng-model'] = 'searchTerm'
        input_attrs['autocomplete'] = "off"
        input_attrs['ng-change'] = 'onChange($event)'
        input_attrs['class'] = 'form-control'
        input_attrs['placeholder'] = 'Type to search'
        self.choices = []
        field = super(SelectMultiple, self).render(name, value, attrs=attrs)
        if 'required' in self.attrs:
            input_attrs['ng-required'] = '!%s.length'%(self.attrs['ng-model'])
            del self.attrs['required']
        text_input = super(Autocomplete, self).render('', '', attrs=input_attrs)
        count = self.autocomplete_view.get_queryset()[:self.autocomplete_view.rows_count + 1].count()
        _json = []
        if count < self.autocomplete_view.rows_count + 1:
            data = []
            for item in self.autocomplete_view.get_data()["data"]:
                data.append({'id': item[0], 'unicode': ' '.join(item[1:])})
            _json = json.dumps(data)
        return render_to_string('ui/multiselect.html', {'attrs': self.attrs,
                                                     'total_count': count,
                                                     'initial_json': _json,
                                                     'name': name,
                                                     'field': field,
                                                     'ng_model': self.attrs['ng-model'],
                                                     'url': self.autocomplete_view.get_url(),
                                                     'text_input': text_input,
                                                     'scope_id':attrs.get('scope_id',name)})

    def value_from_datadict(self, data, files, name):
        value = super(MultiSelect, self).value_from_datadict(data, files, name)
        if value:
            value = json.loads(value[0])
        if not value:
            return ''
        return value
