from django.forms import widgets

class CurrencyInput(widgets.TextInput):
    def render(self, name, value, attrs=None):
        self.attrs['ng-currency'] = ''
        self.attrs['string-to-number'] = ''
        return super(CurrencyInput, self).render(name, value, attrs=attrs)