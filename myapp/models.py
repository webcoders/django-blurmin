# Create your models here.

from ui import models

from ui.models import RichTextField, CurrencyField
from ui.models import CharField,DateField,EmailField, BooleanField,DecimalField,PositiveIntegerField


class Person(models.Model):
    first_name = CharField(max_length=100, verbose_name=u'First name' )
    #mask = "(999)AAAA-(99999)"
    last_name = CharField(max_length=100, verbose_name=u'Last name', autocomplete=True)
    date = DateField(verbose_name="Date of birthday", help_text="Help text for birthday")
    email = EmailField()
    age = PositiveIntegerField()
    sex = BooleanField(verbose_name='Sex',)
    #TODO: Cannot use choice because of absence ui_form.TypedChoiceField
    # choices = ((False, 'Female'), (True, 'Male'))
    revenue = CurrencyField(verbose_name="Revenue (US dollars)", max_digits=10, decimal_places=2)
    page_content = RichTextField()

class Phone(models.Model):
    Person = models.ForeignKey(Person)
    phone = CharField(max_length=100, verbose_name="Phone Number")
