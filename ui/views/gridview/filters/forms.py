from django import forms
from ui.forms.form import Form
from ui import forms as ui_forms
from ui import models as ui_models
from ui.models.utils import get_model_field_from_path
from ui.views.autocomplete import AutocompleteView
from ui.widgets.autocomplete import Autocomplete


class DateFilterForm(Form):
    filter = forms.HiddenInput()


class EqualFilterForm(Form):
    filter = ui_forms.ChoiceField(choices=[])

    def __init__(self, choices=None, field=None, *args, **kwargs):
        if choices:
            if isinstance(field, ui_models.BooleanField):
                self.base_fields['filter'] = ui_forms.TypedChoiceField(required=True, label='', choices=field.choices)
            else:
                self.base_fields['filter'] = ui_forms.ChoiceField(required=True, label='', choices=choices)
        else:
            self.base_fields['filter'] = ui_forms.CharField(max_length=256)
        super(EqualFilterForm, self).__init__(*args, **kwargs)


class AutocompeleteEqualFilterForm(Form):
    filter = ui_forms.CharField()

    class _AutocompleteView(AutocompleteView):
        url = ''

        def __init__(self, url, *args, **kwargs):
            self.url = url
            super(AutocompleteView, self).__init__(*args, **kwargs)

        def get_url(self):
            return self.url

    def __init__(self, url=None, choices=None, field=None, *args, **kwargs):
        if url:
            self.base_fields['filter'] = ui_forms.CharField(label='', autocomplete_view=self._AutocompleteView(url), max_length=256)
        super(AutocompeleteEqualFilterForm, self).__init__(*args, **kwargs)


class DateRangeFilterForm(Form):
    date_from = ui_forms.DateField(required=True, help_text='', label='', placeholder='Date From')
    date_to = ui_forms.DateField(required=True, help_text='', label='', placeholder='Date To')


class DateChoiceFilterForm(Form):
    date = ui_forms.DateField(required=True, help_text='', label='', placeholder='Date')
