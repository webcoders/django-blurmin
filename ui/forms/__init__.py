import json

from copy import deepcopy
from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.db.models.fields.related import ForeignKey
from django.forms.boundfield import BoundField
from django.utils.safestring import mark_safe

from ui.views.autocomplete import AutocompleteView
from ui.widgets import dateinput, Widget, BootstrapWidget, currency, richtext, radioselect, image
from ui.widgets.autocomplete import Autocomplete, SingleSelect
from ui.widgets.multiselect import MultiSelect


# Overriden because default has '-' separator, but we cannot use '-'
# sign for the js var name i.e ng-model definition, so we just have to use underscore '_'
from ui.widgets.switch import Switch


def add_prefix(prefix, field_name):
    return '%s_%s' % (prefix, field_name) if prefix else field_name


class UiBoundField(BoundField):
    def as_formgroup(self):
        self.field.widget.__class__ = type('BootstrapWidgetClass', (BootstrapWidget, self.field.widget.__class__), {})
        return mark_safe(self.as_widget())


class BaseMixin(object):
    def __init__(self, readonly=False, label_position="vertical", *args, **kwargs):
        super(BaseMixin, self).__init__(*args, **kwargs)
        self.widget.__class__ = type('WidgetClass', (Widget, self.widget.__class__), {})
        self.widget.label = ''
        if 'label' in kwargs:
            self.widget.label = kwargs['label']
        self.widget.attrs['label_position'] = label_position
        self.widget.attrs['class'] = ''
        if readonly:
            self.widget.attrs['class'] += 'disabled '
            self.widget.attrs['disabled'] = ''


            # if not editable:
            #     self.widget.attrs['readonly'] = 'readonly'

    def get_bound_field(self, form, field_name):
        return UiBoundField(form, self, field_name)

class BaseInput(BaseMixin):
    def __init__(self, mask=None, placeholder=None, title=None, *args, **kwargs):
        super(BaseInput, self).__init__(*args, **kwargs)
        self.widget.attrs['class'] += 'form-control'
        if mask:
            self.widget.attrs['ui-mask'] = mask
        if placeholder:
            self.widget.attrs['placeholder'] = placeholder
        if title:
            self.widget.attrs['title'] = title

class BaseRegexField(BaseMixin):
    def __init__(self, pattern=None, *args, **kwargs):
        super(BaseRegexField, self).__init__(*args, **kwargs)
        if pattern:
            self.widget.attrs['ng-pattern'] = pattern


class InputField(BaseInput, forms.CharField):
    pass
    # def __init__(self, mask=None, placeholder=None, title=None, *args, **kwargs):
    #     super(InputField, self).__init__(*args, **kwargs)
    #     self.widget.attrs['class'] += 'form-control'
    #     if mask:
    #         self.widget.attrs['ui-mask'] = mask
    #     if placeholder:
    #         self.widget.attrs['placeholder'] = placeholder
    #     if title:
    #         self.widget.attrs['title'] = title


class RegexField(BaseRegexField, forms.CharField):
    pass
    # def __init__(self, pattern=None, *args, **kwargs):
    #     super(RegexField, self).__init__(*args, **kwargs)
    #     if pattern:
    #         self.widget.attrs['ng-pattern'] = pattern


class CharField(RegexField, InputField):
    def __init__(self, autocomplete_view=None, *args, **kwargs):
        if autocomplete_view:
            kwargs['widget'] = Autocomplete
        super(CharField, self).__init__(*args, **kwargs)
        if autocomplete_view:
            self.widget.autocomplete_view = autocomplete_view


class DateField(BaseRegexField, BaseInput, forms.DateField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = dateinput.DateInput
        super(DateField, self).__init__(*args, **kwargs)
        self.widget.attrs['class'] += 'form-control'


class DateTimeField(RegexField, InputField, forms.DateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = dateinput.DateTimeInput
        super(DateTimeField, self).__init__(*args, **kwargs)
        self.widget.attrs['class'] += 'form-control'


class TimeField(RegexField, InputField, forms.TimeField):
    def __init__(self, *args, **kwargs):
        super(TimeField, self).__init__(widget=dateinput.TimeInput, *args, **kwargs)
        self.widget.attrs['class'] += 'form-control'


class IntegerField(BaseMixin, forms.IntegerField):
    def __init__(self, *args, **kwargs):
        super(IntegerField, self).__init__(*args, **kwargs)
        self.widget.attrs['ng-pattern'] = '/.*/'
        self.widget.attrs['class'] += 'form-control'


class PositiveIntegerField(BaseMixin, forms.IntegerField):
    def __init__(self, *args, **kwargs):
        super(PositiveIntegerField, self).__init__(*args, **kwargs)
        self.widget.attrs['ng-pattern'] = '/.*/'
        self.widget.attrs['class'] += 'form-control'


class FloatField(BaseMixin, forms.FloatField):
    def __init__(self, *args, **kwargs):
        super(FloatField, self).__init__(*args, **kwargs)
        self.widget.attrs['ng-pattern'] = '/.*/'
        self.widget.attrs['class'] += 'form-control'


class DecimalField(BaseMixin, forms.DecimalField):
    def __init__(self, *args, **kwargs):
        super(DecimalField, self).__init__(*args, **kwargs)
        self.widget.attrs['ng-pattern'] = '/.*/'
        self.widget.attrs['class'] += 'form-control'


class EmailField(BaseMixin, forms.EmailField):
    def __init__(self, *args, **kwargs):
        super(EmailField, self).__init__(*args, **kwargs)
        self.widget.attrs['ng-pattern'] = '/.*/'
        self.widget.attrs['class'] += 'form-control'


class URLField(BaseMixin, forms.URLField):
    def __init__(self, *args, **kwargs):
        super(URLField, self).__init__(*args, **kwargs)
        self.widget.attrs['ng-pattern'] = '/.*/'
        self.widget.attrs['class'] += 'form-control'


class ChoiceField(BaseMixin, forms.ChoiceField):
    def __init__(self, title=None, *args, **kwargs):
        super(ChoiceField, self).__init__(*args, **kwargs)
        self.widget.attrs['ng-pattern'] = '/.*/'
        self.widget.attrs['class'] = 'form-control selectpicker with-search'
        self.widget.attrs['data-live-search'] = "true"
        self.widget.attrs['selectpicker'] = ""
#TODO this is wrong always adding emtpy option, it is left for gridview equal filter to work
        empty = None
        for c in self.choices:
            if not c[0]:
               empty = c[1]
               break
        if not empty:
            empty = '--------'
            self.choices = [('', empty)] + self.choices


class BooleanField(BaseMixin, forms.BooleanField):

    widget = Switch

    def __init__(self, choices={'Yes': True, 'No': False}, *args, **kwargs):
        super(BooleanField, self).__init__(*args, **kwargs)
        self.widget.choices = choices


class TypedChoiceField(BaseMixin, forms.TypedChoiceField):
    def __init__(self, *args, **kwargs):
        defaults = {'widget': radioselect.RadioSelect}
        defaults.update(kwargs)
        super(TypedChoiceField, self).__init__(*args, **defaults)
        self.widget.attrs['class'] = 'choice'


class RelatedModelField(BaseMixin, forms.Field):
    related_model = None
    related_field = None

    def __init__(self, related_model, *args, **kwargs):
        self.related_model = related_model
        super(RelatedModelField, self).__init__(*args, **kwargs)

    def check_relation(self, model):
        for field in self.related_model._meta.fields:
            if isinstance(field, ForeignKey) and field.rel.to == model:
                self.related_field = field
        if not self.related_field:
            raise ValueError('Model %s has not foreign field for %s' % (self.related_model, model))


class ModelMultipleChoiceField(BaseMixin, forms.ModelMultipleChoiceField):
    def __init__(self, **kwargs):
        search_fields = None
        display_fields = None
        defaults = {}
        if 'search_fields' in kwargs:
            search_fields = kwargs['search_fields']
            del kwargs['search_fields']
        if 'display_fields' in kwargs:
            display_fields = kwargs['display_fields']
            del kwargs['display_fields']
        if search_fields and display_fields:
            defaults = {'widget': MultiSelect}
        defaults.update(kwargs)
        super(ModelMultipleChoiceField, self).__init__(**defaults)
        if search_fields:
            self.widget.autocomplete_view = AutocompleteView(queryset=kwargs['queryset'],
                                                             search_fields=search_fields,
                                                             display_fields=display_fields)
            self.widget.autocomplete_view.rows_count = 30

class ModelChoiceField(BaseMixin, forms.ModelChoiceField):
    def __init__(self, **kwargs):
        search_fields = None
        display_fields = None
        defaults = {}
        if 'search_fields' in kwargs:
            search_fields = kwargs['search_fields']
            del kwargs['search_fields']
        if 'display_fields' in kwargs:
            display_fields = kwargs['display_fields']
            del kwargs['display_fields']
        if search_fields and display_fields:
            defaults = {'widget': SingleSelect}
        defaults.update(kwargs)
        super(ModelChoiceField, self).__init__(**defaults)
        self.widget.attrs['class'] += 'form-control selectpicker with-search'
        self.widget.attrs['data-live-search'] = "true"
        self.widget.attrs['selectpicker'] = ""
        if search_fields:
            self.widget.autocomplete_view = AutocompleteView(queryset=deepcopy(kwargs['queryset']),
                                                             search_fields=search_fields,
                                                             display_fields=display_fields)



# class RelatedMultipleChoiceField(RelatedModelField, MultipleChoiceField):
#     def __init__(self, related_model, search_fields, **kwargs):
#         autocomplete_view = AutocompleteView(related_model, search_fields=search_fields)
#         super(RelatedMultipleChoiceField, self).__init__(related_model=related_model,
#                                                          autocomplete_view=autocomplete_view, **kwargs)


class RichTextField(BaseMixin, forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = richtext.RichText
        super(RichTextField, self).__init__(*args, **kwargs)


class CurrencyField(BaseMixin, forms.DecimalField):
    def __init__(self, *args, **kwargs):
        super(CurrencyField, self).__init__(widget=currency.CurrencyInput, *args, **kwargs)
        self.widget.attrs['class'] += 'form-control'


class ImageField(BaseMixin, forms.CharField):
    def __init__(self, *args, **kwargs):
        super(ImageField, self).__init__(widget=image.ImageInput, *args, **kwargs)
        self.widget.attrs['class'] += 'form-control'


class SlugField(BaseMixin, forms.SlugField):
    def __init__(self, *args, **kwargs):
        super(SlugField, self).__init__(*args, **kwargs)
        self.widget.attrs['class'] += 'form-control'
