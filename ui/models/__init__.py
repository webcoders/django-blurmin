from django.db import models
from django.db.models.fields.files import ImageFieldFile
from django.forms.models import model_to_dict
from django.utils.module_loading import import_string
from django.conf import settings
from ui import forms as ui_forms
from ui.views.autocomplete import AutocompleteView

Manager = models.Manager

class CharField(models.CharField):

    autocomplete = False
    autocomplete_class = AutocompleteView
    mask = None

    def __init__(self, mask=None, autocomplete=False, autocomplete_class=None, *args, **kwargs):
        self.mask = mask
        if autocomplete:
            self.autocomplete = autocomplete
            if autocomplete_class:
                self.autocomplete_class = autocomplete_class
            if not issubclass(self.autocomplete_class, AutocompleteView):
                raise ValueError('Autocomplete class must be subclass of AutocompleteView')
        super(CharField, self).__init__(*args, **kwargs)


    def formfield(self, **kwargs):
        defaults = {'form_class': ui_forms.CharField, 'mask': self.mask , 'choices_form_class': ui_forms.TypedChoiceField }
        if self.autocomplete:
            defaults['autocomplete_view'] = self.autocomplete_class(queryset=self.model.objects.all(), search_fields=[self.name])
        defaults.update(kwargs)
        return super(CharField, self).formfield(**defaults)

class DateTimeField(models.DateTimeField):
    def formfield(self, **kwargs):
        defaults = {'form_class': ui_forms.DateTimeField, 'choices_form_class': ui_forms.TypedChoiceField }
        defaults.update(kwargs)
        return super(DateTimeField, self).formfield(**defaults)

class DateField(models.DateField):
    def formfield(self, **kwargs):
        defaults = {'form_class': ui_forms.DateField, 'choices_form_class': ui_forms.TypedChoiceField }
        defaults.update(kwargs)
        return super(DateField, self).formfield(**defaults)

class TimeField(DateTimeField):
    def formfield(self, **kwargs):
        defaults = {'form_class': ui_forms.TimeField, 'choices_form_class': ui_forms.TypedChoiceField }
        defaults.update(kwargs)
        return super(TimeField, self).formfield(**defaults)

class IntegerField(models.IntegerField):
    def formfield(self, **kwargs):
        defaults = {'form_class': ui_forms.IntegerField, 'choices_form_class': ui_forms.TypedChoiceField }
        defaults.update(kwargs)
        return super(IntegerField, self).formfield(**defaults)

class PositiveIntegerField(models.PositiveIntegerField):
    def formfield(self, **kwargs):
        defaults = {'form_class': ui_forms.IntegerField, 'choices_form_class': ui_forms.TypedChoiceField }
        defaults.update(kwargs)
        return super(PositiveIntegerField, self).formfield(**defaults)

class SmallIntegerField(models.SmallIntegerField):
    def formfield(self, **kwargs):
        defaults = {'form_class': ui_forms.IntegerField, 'choices_form_class': ui_forms.TypedChoiceField }
        defaults.update(kwargs)
        return super(SmallIntegerField, self).formfield(**defaults)

class PositiveSmallIntegerField(models.PositiveSmallIntegerField):
    def formfield(self, **kwargs):
        defaults = {'form_class': ui_forms.IntegerField, 'choices_form_class': ui_forms.TypedChoiceField }
        defaults.update(kwargs)
        return super(PositiveSmallIntegerField, self).formfield(**defaults)

class FloatField(models.FloatField):
    def formfield(self, **kwargs):
        defaults = {'form_class': ui_forms.FloatField, 'choices_form_class': ui_forms.TypedChoiceField }
        defaults.update(kwargs)
        return super(FloatField, self).formfield(**defaults)

class DecimalField(models.DecimalField):
    def formfield(self, **kwargs):
        defaults = {'form_class': ui_forms.DecimalField, 'choices_form_class': ui_forms.TypedChoiceField }
        defaults.update(kwargs)
        return super(DecimalField, self).formfield(**defaults)

class EmailField(models.EmailField):
    def formfield(self, **kwargs):
        defaults = {'form_class': ui_forms.EmailField, 'choices_form_class': ui_forms.TypedChoiceField }
        defaults.update(kwargs)
        return super(EmailField, self).formfield(**defaults)

class URLField(models.URLField):
    def formfield(self, **kwargs):
        defaults = {'form_class': ui_forms.URLField, 'choices_form_class': ui_forms.TypedChoiceField }
        defaults.update(kwargs)
        return super(URLField, self).formfield(**defaults)

# class NullBooleanField(models.BooleanField):
#
#     def formfield(self, **kwargs):
#         kwargs['initial'] = None
#         if not self.choices:
#             self.choices = ((True, 'Yes'), (False, 'No'))
#         defaults = {'choices_form_class': ui_forms.TypedChoiceField, 'form_class': ui_forms.TypedChoiceField}
#         defaults.update(kwargs)
#         return super(NullBooleanField, self).formfield(**defaults)

class BooleanField(models.BooleanField):

    def formfield(self, **kwargs):
        defaults = {'form_class': ui_forms.BooleanField, 'choices_form_class': ui_forms.TypedChoiceField }
        defaults.update(kwargs)
        return super(BooleanField, self).formfield(**defaults)


class ChoiceField(models.CharField):
    def formfield(self, **kwargs):
        defaults = {'form_class': ui_forms.ChoiceField, }
        defaults.update(kwargs)
        return super(ChoiceField, self).formfield(**defaults)

class SlugField(models.SlugField):
    def formfield(self, **kwargs):
        defaults = {'form_class': ui_forms.SlugField, 'choices_form_class': ui_forms.TypedChoiceField }
        defaults.update(kwargs)
        return super(SlugField, self).formfield(**defaults)

class ForeignKey(models.ForeignKey):
    def formfield(self, **kwargs):
        defaults = {'form_class': ui_forms.ModelChoiceField }
        defaults.update(kwargs)
        return super(ForeignKey, self).formfield(**defaults)


class TextField(models.TextField):
    pass

class RichTextField(models.TextField):
    def formfield(self, **kwargs):
        defaults = {'form_class': ui_forms.RichTextField, 'choices_form_class': ui_forms.TypedChoiceField }
        defaults.update(kwargs)
        return super(RichTextField, self).formfield(**defaults)


class CurrencyField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        super(CurrencyField, self).__init__(*args, **kwargs)
    def formfield(self, **kwargs):
        defaults = {'form_class': ui_forms.CurrencyField, 'choices_form_class': ui_forms.TypedChoiceField }
        defaults.update(kwargs)
        return super(CurrencyField, self).formfield(**defaults)


class ManyToManyField(models.ManyToManyField):

    search_fields = None
    display_fields = None

    def __init__(self, *args, **kwargs):
        if 'search_fields' in kwargs:
            self.search_fields = kwargs['search_fields']
        if 'display_fields' in kwargs:
            self.display_fields = kwargs['display_fields']
        super(ManyToManyField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'form_class': ui_forms.ModelMultipleChoiceField}
        if self.search_fields:
            defaults['search_fields'] = self.search_fields
        if self.display_fields:
            defaults['display_fields'] = self.display_fields
        defaults.update(kwargs)
        return super(ManyToManyField, self).formfield(**defaults)


class ForeignKey(models.ForeignKey):

    search_fields = None
    display_fields = None

    def formfield(self, **kwargs):
        defaults = {'form_class': ui_forms.ModelChoiceField}
        if self.search_fields:
            defaults['search_fields'] = self.search_fields
        if self.display_fields:
            defaults['display_fields'] = self.display_fields
        defaults.update(kwargs)
        return super(ForeignKey, self).formfield(**defaults)


class OneToOneField(models.OneToOneField):
    search_fields = None
    display_fields = None

    def formfield(self, **kwargs):
        defaults = {'form_class': ui_forms.ModelChoiceField}
        if self.search_fields:
            defaults['search_fields'] = self.search_fields
        if self.display_fields:
            defaults['display_fields'] = self.display_fields
        defaults.update(kwargs)
        return super(OneToOneField, self).formfield(**defaults)



class ImageFieldFile(ImageFieldFile):
    pass

class ImageField (models.ImageField):
    def formfield(self, **kwargs):
        defaults = {'form_class': ui_forms.ImageField}
        defaults.update(kwargs)
        return super(ImageField, self).formfield(**defaults)

class StatusField(ForeignKey):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('to', import_string(settings.STATUS_MODEL_CLASS))
        super(StatusField, self).__init__(*args, **kwargs)

class Model(models.Model):

    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)
        self._initial = self._dict

    @property
    def diff(self):
        d1 = self._initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    def get_field_diff(self, field_name):
        """
        Returns a diff for field if it's changed and None otherwise.
        """
        return self.diff.get(field_name, None)

    def save(self, *args, **kwargs):
        """
        Saves model and set initial state.
        """
        super(Model, self).save(*args, **kwargs)
        self._initial = self._dict

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in
                             self._meta.fields])

    class Meta:
        abstract = True
