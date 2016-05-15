#!usr/bin/env python

'''
a script to handle importing of more than a single day's data
'''

import django
import os, sys

sys.path.append("../..")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

import json
import re
import datetime
from main.models import Store, Unicorn
django.setup()


def import_unicorns():
    '''
    loops through our directory of JSON files and unpacks each dict
    into a Django object for storage in PostgreSQL.

    Ultimately this will include a foreign key relationship to the
    stores data but for now they can be joined through store_id
    '''
    # Unicorn.objects.all().delete()
    for fp in os.listdir('../data/unicorns_json'):
        j = json.load(open('../data/unicorns_json/' + fp, 'r'))
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
                except Exception:
                    u.store = Store.objects.get(store_id=str(unicorn['store_id']), store_data_date='2016-04-10')
                u.save()

            except Exception as e:
                print e
                print fp
                print unicorn
                continue


def import_stores():
    '''
    unpacks JSON objects of retail-store data into Django counterparts
    for PostgreSQL storage
    '''
    # Store.objects.all().delete()
    stores_by_hand = [{"address": "56 GREENFIELD AVE, ARDMORE, PA",
                       "hours": [{"Sun": "Closed"},
                                 {"Mon": "Closed"},
                                 {"Tue": "Closed"},
                                 {"Wed": "Closed"},
                                 {"Thu": "Closed"},
                                 {"Fri": "Closed"},
                                 {"Sat": "Closed"}],
                       "id": "4602",
                       "latitude": 40.008939,
                       "longitude": -75.297236,
                       "phone": "610.645.5010",
                       "store_type": "Premium Collection"},
                      {"address": "6518 ROUTE 22, STE 444, DELMONT, PA",
                       "hours": [{"Sun": "Closed"},
                                 {"Mon": "Closed"},
                                 {"Tue": "Closed"},
                                 {"Wed": "Closed"},
                                 {"Thu": "Closed"},
                                 {"Fri": "Closed"},
                                 {"Sat": "Closed"}],
                       "id": "6512",
                       "latitude": 40.401738,
                       "longitude": -79.585302,
                       "phone": "724.468.8667",
                       "store_type": "Regular-ass store"},
                      {"address": "401 FRANKLIN MILLS CIR, PHILADELPHIA, PA",
                       "hours": [{"Sun": "Closed"},
                                 {"Mon": "Closed"},
                                 {"Tue": "Closed"},
                                 {"Wed": "Closed"},
                                 {"Thu": "Closed"},
                                 {"Fri": "Closed"},
                                 {"Sat": "Closed"}],
                       "id": "5133",
                       "latitude": 40.085497,
                       "longitude": -74.964900,
                       "phone": "215.281.2080",
                       "store_type": "Premium Collection"}]

    for fp in os.listdir('../data/stores'):
        file_date_pattern = '((?<=\-)\d+.*(?=\.))'
        file_date = re.search(file_date_pattern, fp).group()
        j = json.load(open('../data/stores/' + fp, 'r'))
        for store in j:
            Store.objects.get_or_create(store_id=store['id'],
                                        address=store['address'],
                                        hours=store['hours'],
                                        latitude=store['latitude'],
                                        longitude=store['longitude'],
                                        phone=store['phone'],
                                        store_type=store['store_type'],
                                        store_data_date=file_date)

        for store in stores_by_hand:
            Store.objects.get_or_create(store_id=store['id'],
                                        address=store['address'],
                                        hours=store['hours'],
                                        latitude=store['latitude'],
                                        longitude=store['longitude'],
                                        phone=store['phone'],
                                        store_type=store['store_type'],
                                        store_data_date=datetime.date.today().strftime('%Y-%m-%d'))


def migrate():
    import_stores()
    import_unicorns()


if __name__ == '__main__':
    migrate()
