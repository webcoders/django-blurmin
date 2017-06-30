# coding:utf-8 #
from django.core.exceptions import ImproperlyConfigured
from django.forms import models
from django import forms
from django.forms.models import ModelFormOptions
from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe
from ui.forms import RelatedModelField
from django.conf import settings


class FormMixin(object):
    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs['request']
            del kwargs['request']
        super(FormMixin, self).__init__(*args, **kwargs)

    def add_prefix(self, field_name):
        return '%s_%s' % (self.prefix, field_name) if self.prefix else field_name

    def render_errors(self):
        output = []
        output.append('<div class="alert bg-danger closeable" role="alert" ng-show="form.errors"')
        output.append('<span bind-html-compile="form.errors"></span>')
        output.append('</div>')
        return mark_safe('\n'.join(output))

    def as_div(self):
        output = []
        for boundfield in self:
            boundfield.field.widget.label = boundfield.label_tag() if boundfield.field.label else ''
            output.append(boundfield.as_widget())
        return mark_safe(u'\n'.join(output))


class Form(FormMixin, forms.Form):
    pass


class ModelForm(FormMixin, models.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        for name, field in self.base_fields.items():
            if hasattr(field.widget, 'autocomplete_view') and field.widget.autocomplete_view:
                field.widget.autocomplete_view.request = self.request
            #if isinstance(field, RelatedModelField):
            #    field.check_relation(self._meta.model)
            #TODO we must not rely on field name but field type!!
            if name == 'status':
                self._update_status_queryset(name)

    def _update_status_queryset(self,name):
        Status = import_string(settings.STATUS_MODEL_CLASS)

        # --------------------this returns only possible by hierarchy-----------------------
        try:
            if self.instance.id:
                self.fields[name].queryset = getattr(self.instance, name).get_available(
                    user=self.request.user)
            else:
                self.fields[name].queryset = Status.objects.filter_for_instance(self.instance,
                                                                                initial=True,
                                                                                user=self.request.user)
        except AttributeError:
            self.fields[name].queryset = Status.objects.filter_for_instance(self.instance,
                                                                            initial=True,
                                                                            user=self.request.user)

    def save(self, commit=True):
        ret = super(ModelForm,self).save(commit=commit)
        # TODO we must not rely on field name but field type!!
        if self.fields.get('status', False):
            self._update_status_queryset('status')
        return ret

    def validate_status(self, field_name, cleaned_data):
        Status = import_string(settings.STATUS_MODEL_CLASS)
        if hasattr(self.instance, field_name) and not cleaned_data[field_name].validate(
                getattr(self.instance, field_name), user=self.request.user):
            if self.instance.id:
                possible_statuses = getattr(self.instance, field_name).get_available(user=self.request.user)
            else:
                possible_statuses = Status.objects.get_for_instance(self.instance, initial=True, user=self.request.user)
            st = ' or '.join([unicode(status) for status in possible_statuses])
            message = 'The next status should be %s.' % st
            if not st:
                message = 'The current status "%s" is the last.' % getattr(self.instance, field_name)
            self._errors[field_name] = self.error_class("Invalid status. %s" % message)
            del cleaned_data[field_name]
        return cleaned_data


class ModelFormSet(ModelForm):
    model_form_classes = []
    _model_forms = {}
    def __init__(self, *args, **kwargs):
        parent_form_fields = None
        for cls in self.__class__.__bases__:
            if hasattr(cls, 'Meta'):
                opts = ModelFormOptions(getattr(cls, 'Meta'))
                parent_form_fields = opts.fields
        if parent_form_fields:
            for field in self.base_fields.keys():
                if not field in parent_form_fields:
                    del self.base_fields[field]
        self._base_fields = self.base_fields.copy()
        for cls in self.model_form_classes:
            if issubclass(cls, ModelFormSet):
                raise ImproperlyConfigured('Child class %s can not be subclass of ModelFormSet' % cls)
            name = cls.__name__.lower()
            self._model_forms[name] = cls(*args, **kwargs)
            form = self._model_forms[name]
            self.base_fields.update(form.fields)
        super(ModelFormSet, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        for form in self._model_forms.values():
            form.cleaned_data = self.cleaned_data
            form.save(commit=commit)
        return super(ModelFormSet, self).save(commit=commit)

    def clean(self):
        for form in self._model_forms.values():
            form.data = self.data
            form.clean()
        return super(ModelFormSet, self).clean()

    def is_valid(self):
        is_valid = True
        for form in self._model_forms.values():
            form.data = {}
            for key, value in self.data.items():
                if key in form.fields:
                    form.data[key] = value
            if not form.is_valid():
                is_valid = False
        if not super(ModelFormSet, self).is_valid():
            is_valid = False
        return is_valid