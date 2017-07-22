# Create your models here.

from ui import models

from ui.models import RichTextField, CurrencyField
from ui.models import CharField,DateField,EmailField, BooleanField,DecimalField,PositiveIntegerField


class Person(models.Model):
    first_name = CharField(max_length=100, verbose_name=u'First name' )
    last_name = CharField(max_length=100, verbose_name=u'Last name', autocomplete=True)
    date = DateField(verbose_name="Date of birthday", help_text="Help text for birthday")
    email = EmailField()
    public_email = BooleanField(verbose_name='Public email',default=False)
    age = PositiveIntegerField()
    skill = PositiveIntegerField(choices=((1,'Beginner'),(2,'Professional'),(3,'Expert')),default=1)
    sex = models.CharField(choices = (('F', 'Female'), ('M', 'Male')),default='M',max_length=1)
    revenue = CurrencyField(verbose_name="Revenue (US dollars)", max_digits=10, decimal_places=2)
    page_content = RichTextField()

class Phone(models.Model):
    Person = models.ForeignKey(Person)
    phone = CharField(max_length=100, verbose_name="Phone Number",mask = "(999)999-99-99")
