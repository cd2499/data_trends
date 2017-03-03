from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
import datetime
from django.forms import ModelForm


# Create your models here.
class CarMake(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return u'%s' % self.name

class CarModel(models.Model):
    name = models.CharField(max_length=100)
    carmake = models.ForeignKey(CarMake)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return u'%s' % self.name

class CarYear(models.Model):
    name = models.CharField(max_length=4)
    carmodel = models.ForeignKey(CarModel)
    
    class Meta:
        ordering = ('name',)

    def __str__(self):
        return u'%s' % self.name

class GetCar(models.Model):
    carmake = models.ForeignKey(CarMake)
    carmodel = models.ForeignKey(CarModel)
    caryear = models.ForeignKey(CarYear)

