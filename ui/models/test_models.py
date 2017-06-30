# coding: utf-8
from django.db import models

from ui.models import RichTextField, CurrencyField
from ui.models import CharField,DateField,EmailField, BooleanField,DecimalField,PositiveIntegerField


class Test(models.Model):
    first_name = CharField(max_length=100, verbose_name=u'Имя' )
    #mask = "(999)AAAA-(99999)"
    last_name = CharField(max_length=100, verbose_name=u'Фамилия', autocomplete=True)
    date = DateField(verbose_name="Date of birthday", help_text="Help text for birthday")
    email = EmailField()
    age = PositiveIntegerField()
    sex = BooleanField(verbose_name='Sex', choices=((False, 'Female'), (True, 'Male')))
    revenue = CurrencyField(verbose_name="Revenue (US dollars)", max_digits=10, decimal_places=2)
    page_content = RichTextField()

class Phone(models.Model):
    test = models.ForeignKey(Test)
    phone = CharField(max_length=100, verbose_name="Phone Number")

