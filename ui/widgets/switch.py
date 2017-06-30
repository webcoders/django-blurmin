from django.forms import widgets
from django.utils import six

class Switch(widgets.HiddenInput):
    def render(self, name, value, attrs=None):
        yes_text = 'Yes'
        no_text = 'No'
        for k, v in self.choices.items():
            if v == True:
                yes_text = k
            if v ==False:
                no_text = k

        field = super(Switch, self).render(name, value, attrs=attrs)
        return """<input bs-switch switch-on-text="%(YES)s" switch-off-text="%(NO)s" switch-animate="true" type="checkbox" ng-model="%(ng-model)s"/>%(field)s""" \
               % {'ng-model': self.attrs['ng-model'], 'field': field, 'YES': yes_text, 'NO': no_text}


    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        # Translate true and false strings to boolean values.
        values = {'true': True, 'false': False}
        if isinstance(value, six.string_types):
            value = values.get(value.lower(), value)
        return bool(value)
