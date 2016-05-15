#!usr/bin/env python

import django
import os, sys

sys.path.append("../..")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

import json
from main.models import Store, Unicorn
django.setup()


def import_unicorns(filepath):
    '''
    called from pdf_multi_plcb_product_getter.py

    given our daily scraped data, passes it into our
    PostgreSQL time-series table
    '''
    j = json.load(open(filepath, 'r'))
    for unicorn in j:
        try:
            u = Unicorn()
            u.product_id = unicorn['product_code']
            u.name = unicorn['name']
            u.num_bottles = unicorn['bottles']
            u.bottle_size = unicorn['bottle_size']
            u.price = unicorn['price']
            u.on_sale = unicorn['on_sale']
            u.on_sale_price = unicorn['on_sale']
            u.scrape_date = unicorn['scrape_date']
            try:
                u.store = Store.objects.get(store_id=str(unicorn['store_id']), store_data_date='2016-05-15')
            except Store.DoesNotExist:
                u.store = Store.objects.get(store_id=str(unicorn['store_id']), store_data_date='2016-04-10')
            except Exception as e:
                print 'Something wrong with the unicorn store: ', e, unicorn
                u.store = None
            u.save()

        except (KeyError, ValueError) as e:
            print 'Something wrong with the unicorn: ', e, unicorn


def import_stores(filepath):
    '''
    a function to use infrequently, whenever we need to update stores data
    '''
    Store.objects.all().delete()

    j = json.load(open(filepath, 'r'))
    for store in j:
        s = Store.objects.get_or_create(store_id=store['id'],
                                        address=store['address'],
                                        hours=store['hours'],
                                        latitude=store['latitude'],
                                        longitude=store['longitude'],
                                        phone=store['phone'],
                                        store_type=store['store_type'])


def migrate():
    import_stores()  # s =
    import_unicorns()  # s


if __name__ == '__main__':
    import_unicorns()
