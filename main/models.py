from django.db import models
# from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Store(models.Model):
    store_id = models.CharField(max_length=10)
    address = models.CharField(max_length=255, null=False, blank=False)
    hours = models.CharField(max_length=255, null=False, blank=False)
    latitude = models.FloatField(null=False)
    longitude = models.FloatField(null=False)
    phone = models.CharField(max_length=15, null=False, blank=False)
    store_type = models.CharField(max_length=100, null=True, blank=True)
    store_data_date = models.DateField(null=True, blank=True)
    # county =

    def __unicode__(self):
        return '{}, {}, {}, {}'.format(self.store_id,
                                       self.address,
                                       self.store_type,
                                       self.phone)


class Unicorn(models.Model):
    product_id = models.CharField(max_length=10)
    name = models.CharField(max_length=255, null=False, blank=False)
    num_bottles = models.IntegerField(null=False)
    bottle_size = models.CharField(max_length=10, null=False, blank=False)
    price = models.FloatField(null=False, blank=False)
    on_sale = models.NullBooleanField(null=True, blank=True)
    on_sale_price = models.FloatField(null=True, blank=True)
    scrape_date = models.DateField(null=True, blank=True)
    store = models.ForeignKey('Store', null=True)
    # proof =
    # booze_type =

    def __unicode__(self):
        return '{}'.format(self.name)
