#!usr/bin/env python

'''
a script to handle importing of more than a single day's data
'''

import django
import os, sys

sys.path.append("../..")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

import json
from main.models import Stores, Unicorns
django.setup()


def import_unicorns():  # store_object
    '''
    loops through our directory of JSON files and unpacks each dict
    into a Django object for storage in PostgreSQL.

    Ultimately this will include a foreign key relationship to the
    stores data but for now they can be joined through store_id
    '''
    # Unicorns.objects.all().delete()
    # total_records = []
    for fp in os.listdir('../data/unicorns_json'):
        j = json.load(open('../data/unicorns_json/' + fp, 'r'))
        # for store in store_object:
        for idx, unicorn in enumerate(j):
            # if unicorn['store_id'] in store:
            # print '{} from {}'.format(idx, fp)
            u = Unicorns.objects.create(product_id=unicorn['product_code'],
                                        name=unicorn['name'],
                                        num_bottles=unicorn['bottles'],
                                        bottle_size=unicorn['bottle_size'],
                                        price=unicorn['price'],
                                        on_sale=unicorn['on_sale'],
                                        on_sale_price=unicorn['on_sale'],
                                        store_id=unicorn['store_id'],
                                        scrape_date=unicorn['scrape_date'])

            # total_records.append(u)
            # print 'created {}'.format(u.name)
    # print 'made {} records'.format(len(total_records))


def import_stores():
    '''
    unpacks JSON objects of retail-store data into Django counterparts
    for PostgreSQL storage
    '''
    # Stores.objects.all().delete()

    for fp in os.listdir('../data/stores'):
        j = json.load(open('../data/stores/' + fp, 'r'))
        for store in j:
            s = Stores.objects.get_or_create(store_id=store['id'],
                                             address=store['address'],
                                             hours=store['hours'],
                                             latitude=store['latitude'],
                                             longitude=store['longitude'],
                                             phone=store['phone'],
                                             store_type=store['store_type'])
            # yield s


def migrate():
    import_stores()  # s =
    import_unicorns()  # s


if __name__ == '__main__':
    migrate()
