#!usr/bin/env python

import django
import os, sys

sys.path.append("../..")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

import json
from main.models import Stores, Unicorns
django.setup()


def import_unicorns():  # store_object
    Unicorns.objects.all().delete()

    total_records = []

    # import ipdb; ipdb.set_trace()
    for fp in os.listdir('../data/unicorns_json'):
        # print fp
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
            # try:
            #     u.scrape_date = unicorn['scrape_date']
            # except (KeyError, ValueError) as e:
            #     u.scrape_date = None

            total_records.append(u)
            print 'created {}'.format(u.name)

    print 'made {} records'.format(len(total_records))


def import_stores():
    Stores.objects.all().delete()

    # import ipdb; ipdb.set_trace()
    for fp in os.listdir('../data/stores'):
        # print fp
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
