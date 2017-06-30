import datetime
from copy import deepcopy
from django.db import transaction
from time import sleep
from django.utils.translation import ugettext as _
from channels.channel import Group
import math
from django.utils.decorators import classonlymethod
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
from django.contrib.admin.models import ADDITION, CHANGE
from django.contrib.admin.options import get_content_type_for_model
from django.db.transaction import atomic
from django.forms.models import ModelFormOptions
from django.utils.encoding import smart_text, force_text
from django.utils.module_loading import import_string
from django.views.generic import edit
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin, SingleObjectTemplateResponseMixin, BaseDetailView
from django.forms import models as model_forms
from django.forms import models as _model_forms
from django.http.response import HttpResponse
from django.core.exceptions import ImproperlyConfigured, FieldDoesNotExist
from django.forms.forms import NON_FIELD_ERRORS
from django.core.serializers.json import DjangoJSONEncoder
from ui.exceptions import ObjectIdentifierIsNotDefined
from ui.forms.form import ModelForm, ModelFormSet
from django import forms
from ui import forms as uiforms
from django.http import Http404
from ui.notifications.models import Notification, NotificationRecipient
from ui.serializers.json_encoder import UiJSONEncoder
import json


from django.db import models
from ui.views import BaseView


def ng_get_model(form, initial, as_json=True, readonly_fields=[], render_fields=[]):
    res = {'fields':{},'errors':'','content':{}}
    # for testing form errors look
    # form.errors[NON_FIELD_ERRORS] = form.error_class(["Form level ERROR!","Second ERROR"])
    res['errors'] = str(form.errors[NON_FIELD_ERRORS]) if form.errors.has_key(NON_FIELD_ERRORS) else ''
    def get_model_field(name):
        try:
            if hasattr(form, '_model_forms'):
                forms = form._model_forms.values()
                forms = [form] + forms
                for f in forms:
                    if hasattr(f.Meta, 'model'):
                        try:
                            return (f.Meta.model._meta.get_field(name), f)
                        except FieldDoesNotExist:
                            pass
            elif hasattr(form.Meta, 'model'):
                return (form.Meta.model._meta.get_field(name), form)
        except AttributeError:
            pass
        return None
    def none_value(value):
        return '' if value is None else value

    def get_value_from_modelformset(form):

        value = ''

        if hasattr(form, '_model_forms'):
            _forms = form._model_forms.values()
            _forms = [form] + _forms
            for f in _forms:
                try:
                    if name in f.fields:
                        value = getattr(f.instance, name)
                except AttributeError:
                    value = ''
        else:
            if form.instance and form.instance.pk:
                value = getattr(form.instance, name, '')
        return value

    for name, field in form.fields.items():
        prefixed = form.add_prefix(name).replace('-', '_')
        data_type = field.__class__.__name__.replace('Field', '').lower()
        errors = ''
        try:
            model_field = get_model_field(name)
            if model_field:
                model_field = model_field[0]
        except FieldDoesNotExist:
            model_field = None
        readonly_value = None

        if isinstance(form, ModelForm) and getattr(form.instance, 'id', False) and name in readonly_fields and\
                hasattr(form.instance, name):
            value = getattr(form.instance, name)
        elif isinstance(form, ModelFormSet):
            value = get_value_from_modelformset(form)
        elif hasattr(form, 'cleaned_data'):
            errors = str(form.errors[name]) if form.errors.get(name) else ''
            if name in form.cleaned_data:
                value = form.cleaned_data.get(name)
            else:
                value = form.data.get(prefixed)
                if value is None and form.instance and hasattr(form.instance, name):
                    _f = get_model_field(name)[1]
                    value = getattr(_f.instance, name)
        else:
            if initial.get(name):
                value = initial.get(name)
#TODO this is temporary not for all cases?!
                if getattr(form.instance,name,False):
                   readonly_value = unicode(getattr(form.instance, name))
            elif not form.is_bound and getattr(form, 'instance', False):
                value = get_value_from_modelformset(form)
            else:
                value = field.initial


        if readonly_value is None:
            readonly_value = unicode(none_value(value))
        if not value and field.initial and not form.is_bound:
            value = field.initial
        if value is not None:
            if isinstance(value, models.Model):
                value = value.pk
                if not readonly_value:
                    readonly_value = str(none_value(value))
            if isinstance(field, forms.DecimalField) and value:
                # TODO choice fields data transformation not solved
                    #or isinstance(model_field, models.DecimalField):
                if type(value) == str:
                    value = value.replace(',', '').strip()
                value = float(value)

            elif isinstance(field, forms.IntegerField) and value:
                # TODO choice fields data transformation not solved
                    #or isinstance(model_field, models.IntegerField)
                value = int(value)
            elif isinstance(model_field, models.BooleanField):
                readonly_value = 'Yes' if value else 'No'
            elif isinstance(model_field, models.ForeignKey) and hasattr(model_field, 'search_fields') \
                    and model_field.search_fields and value and hasattr(field.widget,'autocomplete_view'):
                autocomplete = field.widget.autocomplete_view
                autocomplete.queryset = autocomplete.queryset.filter(pk=value)
                data = autocomplete.get_data()
                data_type = 'modelchoice_ac'
                value = json.dumps(data['data'])
            elif isinstance(field, forms.ModelMultipleChoiceField):
                _v = []
                if hasattr(value, 'all'):
                    value = value.all()
                if value != u'[]':
                    for v in value:
                        display_fields = model_field.display_fields or model_field.search_fields
                        display_value = []
                        if display_fields:
                            for f in display_fields:
                                if '__' in f:
                                    _value = v
                                    _f = f.split('__')
                                    for __f in _f:
                                        _value = getattr(_value, __f)
                                else:
                                    _value = getattr(v, f)
                                display_value.append(_value)
                            v = {'id': field.prepare_value(v), 'unicode': ' '.join(display_value)}
                        else:
                            v = {'id': field.prepare_value(v), 'unicode': unicode(v)}
                        _v.append(v)
                value = _v
                readonly_value = ','.join([v['unicode'] for v in value])
            else:
                value = unicode(none_value(value))
        else:
            if hasattr(field, 'queryset'):
                value = []
        if data_type == 'typedchoice' and readonly_value:
           for val in field.choices:
#TODO choice fields data transformation not solved
               if val[0] == value or str(val[0]) == value:
                   readonly_value = val[1]

        if isinstance(field, uiforms.CurrencyField) and (not value or math.isnan(float(value))):
            value = '0.00'
        if hasattr(form, 'get_value_for_' + name):
            value = getattr(form, 'get_value_for_' + name)()
        res['fields'][prefixed] = {'value': value, 'data_type': data_type, 'error' : errors  ,
                                   'help_text': field.help_text, 'is_readonly':(name in readonly_fields), 'readonly_value':readonly_value }

        if render_fields == '__all__' or name in render_fields:
            res['content'][prefixed] = field.get_bound_field(form, name).as_formgroup()

    if isinstance(form, ModelForm) and getattr(form.instance, 'id', False):
        for name in readonly_fields:
            if not name in form.fields and hasattr(form.instance,name):
                value = unicode(none_value(getattr(form.instance,name)))
                prefixed = form.add_prefix(name).replace('-', '_')
                res['fields'][prefixed] = {'value': value, 'data_type': 'textfield', 'error' : '',
                                   'help_text': '', 'is_readonly':True, 'readonly_value':value }

    if len(form.errors):
        _errors = ''
        for field in form:
            if not field.errors:
                continue
            label = field.label + ' - '
            if label == '__all__':
                label = ''
            _errors += '<div style="padding:3px;">' + label + ','.join(field.errors) + '</div>'
        error_line = """
<div>
    <span style="font-weight: bold;" ng-init="errorsCollapsed = true" ng-click="errorsCollapsed = !errorsCollapsed">
    Please correct the errors below
    <i class="glyphicon chevron" style="cursor: pointer; top: 3px; left:5px;"
                ng-class="{'glyphicon-chevron-down': !errorsCollapsed, 'glyphicon-chevron-right': errorsCollapsed}"></i>
    </span>
</div>
<div uib-collapse="errorsCollapsed" style="padding: 7px;">
%s
</div>
        """ % _errors
        res['errors'] += error_line
    if as_json:
        return json.dumps(res, cls=UiJSONEncoder)
    return res



class FormMixin(edit.FormMixin):
# TODO subject for removal, due to use ViewSetMemberMixin instead of parent_view
    parent_view = None
    row_id_field_name = 'id'
    readonly_fields = []
    render_fields = []
    render_fields_exclude = []
    render_form = False
    content_reload_fields = []
    fields = None
    form_type = None #grid-change or change

    def get_form_class(self, **kwargs):
        return self.form_class

    def get_readonly_fields(self):
        return self.readonly_fields;

    def get_content_reload_fields(self):
        return self.content_reload_fields

    def get_fields(self):
        # TODO will not work with no ModelForm
        if self.fields:
            return self.fields
        form = self.get_form_class(fields=None)
        return list(form.base_fields) + list(self.get_readonly_fields())

    # TODO subject for removal, moved to ViewSetMemberMixin
    def get_url_name(self):
        url = self.parent_view.url_name() if self.parent_view else self.__class__.__name__.lower()
        return url

    def get_form_kwargs(self):
        kwargs = super(FormMixin, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_ng_model(self,form,initial, readonly_fields=[],render_fields=[],as_json=True):
        if render_fields != '__all__':
            render_fields = render_fields + self.get_content_reload_fields()
        res = ng_get_model(form, initial, readonly_fields=readonly_fields, render_fields=render_fields, as_json=False)
#TODO filter forms does not have any object or row_id_field_name, may be we need to define
        if ( hasattr(self,'object') and hasattr(self,'row_id_field_name') ):
            res['record_id'] = getattr(self.object, self.row_id_field_name, '') if self.object else ''
        if as_json:
            return json.dumps(res, cls=UiJSONEncoder)
        return res

    def get_render_form(self):
        if self.render_fields or self.render_fields_exclude:
#TODO handle render_fields_exclude!!!!
            fields = self.render_fields
        else:
            fields = self.get_fields()
        if not fields:
            return self.get_form_class()
        return self.get_form_class(fields=fields)

    def get_context_data(self, **kwargs):
        from ui.views.gridview.filters.form_views import FilterFormView
        ctx = super(FormMixin, self).get_context_data(**kwargs)
# Do we need field hiding and readonly fields in filter forms? Now we don'nt.
        if isinstance(self,FilterFormView):
            ctx['ng_model'] = self.get_ng_model(ctx['form'], self.initial,readonly_fields=self.get_readonly_fields())
            return ctx
        ctx['view_name'] = self.get_url_name()
        ctx['view_url'] = self.get_url()
        if self.form_type:
            ctx['form_type'] = self.form_type
        ctx['ng_model'] = self.get_ng_model(ctx['form'], self.initial, readonly_fields=self.get_readonly_fields(),as_json=False)
        ctx['row_id_field_name'] = self.parent_view.row_id_field_name if self.parent_view else self.row_id_field_name
        if self.render_form:
            ctx['render_form'] = self.get_render_form()(request=self.request)
            # we get all form fields correctly as it is normal form render,
            # but we put contents for all possible (render_fields) form fields
            render_ng_model=self.get_ng_model(ctx['render_form'], self.initial,render_fields='__all__',as_json=False)
            ctx['ng_model']['content'] = render_ng_model['content']
        ctx['ng_model'] = json.dumps({'form':ctx['ng_model']}, cls=UiJSONEncoder)
        return ctx

    def form_valid(self, form):
        return HttpResponse(self.get_ng_model(form,self.initial,readonly_fields=self.get_readonly_fields()))
    def form_invalid(self, form):
        return HttpResponse(self.get_ng_model(form,self.initial,readonly_fields=self.get_readonly_fields()))


class GetObjectMixin(object):
    def get_object(self, queryset=None):
        """
        Returns the object the view is displaying.

        By default this requires `self.queryset` and a `pk` or `slug` argument
        in the URLconf, but subclasses can override this to return any object.
        """
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        if not (pk or slug):
            pk = self.request.GET.get(self.pk_url_kwarg)
            slug = self.request.GET.get(self.slug_url_kwarg)

        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by slug.
        if slug is not None and (pk is None or self.query_pk_and_slug):
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        # If none of those are defined, it's an error.
        if pk is None and slug is None:
            raise ObjectIdentifierIsNotDefined("Generic detail view %s must be called with "
                                 "either an object pk or a slug."
                                 % self.__class__.__name__)

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj



class ModelFormMixin(FormMixin, GetObjectMixin, edit.ModelFormMixin):
    def get_form_class(self,**kwargs):
        """
        Returns the form class to use in this view.
        """
        if 'fields' in kwargs:
            fields = kwargs.pop('fields')
        else:
            fields = self.get_fields()

        exclude = []
        # TODO: Need to remove readonly fields from form, but include them when returning by get_ng_model
        # if self.request.method == 'POST':
        #     exclude = self.get_readonly_fields();

        if self.form_class:
            if fields or len(exclude) > 0:
                # TODO make sure it is saving all form_class definitions!!!!!
                if fields == '__all__':
                    fields = ModelFormOptions(self.form_class).fields
                form_class = _model_forms.modelform_factory(self.model, form=self.form_class, fields=fields, exclude=exclude)
            else:
                form_class = self.form_class
        else:
            model = None
            if self.model is not None:
                # If a model has been explicitly provided, use it
                model = self.model
            elif hasattr(self, 'object') and self.object is not None:
                # If this view is operating on a single object, use
                # the class of that object
                model = self.object.__class__
            else:
                # Try to get a queryset and extract the model class
                # from that
                model = self.get_queryset().model

            if fields is None and model is None:
                raise ImproperlyConfigured(
                    "Using ModelFormMixin (base class of %s) without "
                    "the 'fields' attribute is prohibited." % self.__class__.__name__
                )

            form_class  = _model_forms.modelform_factory(model, form=ModelForm, fields=(fields if fields else self.fields),
                                          exclude=exclude)
        for field in self.get_readonly_fields():
            if form_class.base_fields.get(field,False):
                form_class.base_fields[field].required = False
                form_class.base_fields[field].is_disabled = True

        return form_class

class DeleteView(SingleObjectTemplateResponseMixin, GetObjectMixin, BaseDetailView):
    parent_view = None
    row_id_field_name = 'id'
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteView,self).dispatch(request, *args, **kwargs)

    def get_queryset_multi(self,request):
        data = request.POST if request.method == 'POST' else request.GET
        ids = json.loads(data['ids'])
        q_ids = []
        for id in ids:
            q_ids.append(id)
        return self.get_queryset().filter(**{self.row_id_field_name + '__in': q_ids})

    def delete_multi(self, request, *args, **kwargs):
        try:
            self.get_queryset_multi(request).delete()
            # data = request.POST if request.method == 'POST' else request.GET
            # ids = json.loads(data['ids'])
            # q_ids = []
            # for id in ids:
            #     q_ids.append(id)
            # self.get_queryset().filter(**{self.row_id_field_name + '__in':q_ids}).delete()
            return self.delete_success(request, *args, **kwargs)
        except Exception,e:
            return self.delete_fail(request, *args, **kwargs)

    def delete_success(self, request, *args, **kwargs):
        return HttpResponse(json.dumps({'message': 'success'}, cls=DjangoJSONEncoder))
    def delete_fail(self, request, *args, **kwargs):
        return HttpResponse(json.dumps({'message': 'Sorry, fail to delete records'}, cls=DjangoJSONEncoder))

    def delete(self, request, *args, **kwargs):
        if request.GET.get('multi'):
            return self.delete_multi(request, *args, **kwargs)
        try:
            self.object = self.get_object()
            self.object.delete()
            return self.delete_success(request, *args, **kwargs)
        except:
            return self.delete_fail(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # sleep(3)
        return self.delete(request, *args, **kwargs)


class ChangeView(edit.TemplateResponseMixin, ModelFormMixin, edit.ProcessFormView):
    show_notifications = False
    delete_view_class = None
    delete_view_instance = None
    def get(self, request, *args, **kwargs):
        self.object = None
        try:
            self.object = self.get_object()
            form = self.get_form()
            if request.is_ajax():
                return HttpResponse(self.get_ng_model(form, form.initial, readonly_fields=self.get_readonly_fields()))
            else:
                return super(ChangeView, self).get(request, *args, **kwargs)
        except ObjectIdentifierIsNotDefined:
            if request.is_ajax():
                form = self.get_form()
                return HttpResponse(self.get_ng_model(form, form.initial, readonly_fields=self.get_readonly_fields()))
        except Http404 as e:
            return HttpResponse(json.dumps({'errors':['[404] Sorry, the record you are trying to operate no longer exists']}, cls=DjangoJSONEncoder))
        return super(ChangeView, self).get(request, *args, **kwargs)

    def on_dispatch(self,request, *args, **kwargs):
        if self.delete_view_class:
            self.delete_view_instance = self.delete_view_class(**self.get_delete_view_kwargs())
            self.delete_view_instance.request = request

    def dispatch(self, request, *args, **kwargs):
        self.on_dispatch(request, *args, **kwargs)
        # self.form_type = ('grid-change' if 'grid-row' in request.GET else 'change')
        return super(ChangeView,self).dispatch(request, *args, **kwargs)

    def get_delete_view_kwargs(self):
        initial_kwargs = {'model': self.model, 'queryset': self.queryset,
                          'parent_view': self}
        cls = self.get_delete_view_class()
        kwargs = {}
        # prevent overwriting custom view properties, if we use other than ChangeView
        for attr in initial_kwargs:
            if not getattr(cls, attr) and initial_kwargs[attr]:
                kwargs[attr] = initial_kwargs[attr]
        return kwargs

    def get_delete_view_class(self):
        return self.delete_view_class

    def get_delete_view(self):
        return self.get_delete_view_class().as_view(**self.get_delete_view_kwargs())

    def post(self, request, *args, **kwargs):
        if request.path.split('/')[-1] == 'create' or 'create' in request.GET:
            self.object = None
        else:
            self.object = self.get_object()
        return super(ChangeView, self).post(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        ctx = super(ChangeView,self).get_context_data(**kwargs)
        if self.parent_view:
            ctx['grid_view_name'] = self.get_url_name()
        if self.delete_view_instance:
            ctx['delete_view_url'] = self.delete_view_instance.get_url()
        return ctx

    def form_valid(self, form):
        add = True if self.object is None else False
        form.save(commit=False)
        self.object = self.save_model(form, not add)
        # Checking form validation again giving us alternative to add form errors during save_model processing,
        # this was very difficult to show such errors in regular django ModelAdmin
        if form.is_valid():
            return FormMixin.form_valid(self, form)
        else:
            return FormMixin.form_invalid(self, form)
    @atomic
    def save_model(self, form, change):
        old_instance = deepcopy(form.instance)
        instance = form.save()
        if not change or old_instance.has_changed:
            content_type = get_content_type_for_model(old_instance)
            entry_log = import_string(settings.LOGENTRY_MODEL_CLASS)()
            entry_log.user_id = self.request.user.id
            entry_log.content_type_id = content_type.pk
            entry_log.object_id = smart_text(old_instance.pk)
            entry_log.object_repr = force_text(old_instance)[:200] if old_instance.id else ''
            entry_log.action_flag = ADDITION if not change else CHANGE
            changed_fields = []
            for field in old_instance.changed_fields:
                changed_fields.append('"%s"' % instance._meta.get_field(field).verbose_name)
            entry_log.change_message = '' if not change else 'Changed ' + ', '.join(changed_fields)
            entry_log = self.save_entry_log(old_instance, entry_log)
            if old_instance.has_changed and old_instance.id:
                if hasattr(settings,'CHANGELOG_MODEL_CLASS') and settings.CHANGELOG_MODEL_CLASS:
                    for field_name, changes in old_instance.diff.items():
                        change_log = import_string(settings.CHANGELOG_MODEL_CLASS)()
                        change_log.field_name = field_name
                        change_log.log = entry_log
                        change_log.old_value = changes[0]
                        change_log.new_value = changes[1]
                        self.save_change_log(old_instance, change_log)
            if self.show_notifications:
                if change:
                    id = instance.pk
                    if hasattr(instance, 'slug'):
                        id = instance.slug
                    self.send_notification('info', '%s %s' % (content_type.model.title(), id), entry_log.change_message,
                                           instance)
        instance.old_instance = old_instance._initial
        return instance

    def save_entry_log(self, obj, entry_log):
        entry_log.save()
        return entry_log

    def save_change_log(self, obj, change_log):
        change_log.save()
        return change_log

    def get_channels(self):
        return []

    def get_channel_users(self):
        return []

    def send_notification(self, level, title, text, obj):
        from ma.notifications import send_to_recipients
        notification = Notification()
        notification.action_object = obj
        notification.message = text
        notification.title = title
        notification.level = level
        notification.user = self.request.user
        notification.save()

        recipients = []

        for user_id in self.get_channel_users():
            recipient = NotificationRecipient()
            recipient.notification = notification
            recipient.recipient_id = user_id
            recipient.save()
            recipients.append(user_id)


class FormView(FormMixin, edit.FormView):
    pass


