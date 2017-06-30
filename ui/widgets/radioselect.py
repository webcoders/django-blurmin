from django import  forms
class RadioSelect(forms.RadioSelect):
    def render(self, name, value, attrs=None):
        return '<div class="radio-select">' + super(RadioSelect, self).render(name, value, attrs=attrs) + '</div>'
