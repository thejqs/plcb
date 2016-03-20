from django.db import models

# Create your models here.


class Stores(Models.model):
    store_id = models.CharField(max_length=10, primary_key=True,)
    address = models.CharField(max_length=255, null=False, blank=False)
    hours = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.IntegerField
    longitude = models.IntegerField
    phone = models.CharField(max_length=15, null=, blank=True)
    is_premium_collection = models.BooleanField

    def __unicode__(self):
        return '{}'.format(Store.store_id)


class PLCBunicorns(Models.model):

    def __unicode__(self):
        return '{}'.format(XXX)


class Bottles(Models.model):

    def __unicode__(self):
        return '{}'.format(XXX)


class BoozeTypes(Models.model):
    name = models.CharField(max_length=255)
    


    def __unicode__(self):
        return '{}'.format(XXX)
