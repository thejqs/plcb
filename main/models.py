from django.db import models
# from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Stores(models.Model):
    store_id = models.CharField(max_length=10, primary_key=True,)
    address = models.CharField(max_length=255, null=False, blank=False)
    hours = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    store_type = models.CharField(max_length=100, null=True, blank=True)
    # county =

    def __unicode__(self):
        return '{}, {}, {}, {}'.format(self.store_id,
                                        self.address,
                                        self.phone,
                                        self.store_type)


class Unicorns(models.Model):
    product_id = models.CharField(max_length=10)
    name = models.CharField(max_length=255, null=True, blank=True)
    num_bottles = models.IntegerField(null=True)
    bottle_size = models.CharField(max_length=10, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    on_sale = models.NullBooleanField(null=True, blank=True)
    on_sale_price = models.FloatField(null=True, blank=True)
    scrape_date = models.DateField(null=True, blank=True)
    store_id = models.CharField(max_length=10, null=True)
    # proof =
    # booze_type =

    def __unicode__(self):
        return '{}'.format(self.name)


# class Bottles(Models.model):
#
#     def __unicode__(self):
#         return '{}'.format(XXX)
#
#
# class BoozeTypes(Models.model):
#     name = models.CharField(max_length=255)
#
#     def __unicode__(self):
#         return '{}'.format(XXX)
