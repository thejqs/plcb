#!usr/bin/env python

import django
import os, sys

sys.path.append("../..")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

import json
from main.models import Stores, Unicorns
django.setup()


def import_unicorns(filepath):
    """
    given our daily scraped data, passes it into our
    PostgreSQL time-series table
    """
    # Unicorns.objects.all().delete()
    # file_date_pattern = '((?<=\-)\d+.*(?=\.))'
    # file_date = re.search(file_date_pattern, filepath).group()

    j = json.load(open(filepath, 'r'))
    for unicorn in j:
        try:
            u = Unicorns.objects.create(product_id=unicorn['product_code'],
                                        name=unicorn['name'],
                                        num_bottles=unicorn['bottles'],
                                        bottle_size=unicorn['bottle_size'],
                                        price=unicorn['price'],
                                        on_sale=unicorn['on_sale'] if False else True,
                                        on_sale_price=unicorn['on_sale'],
                                        scrape_date=unicorn['scrape_date'],
                                        store_id=unicorn['store_id'])
        except (KeyError, ValueError) as e:
            print e
            print unicorn

        print 'created {}'.format(u.name)


def import_stores(filepath):
    """
    a function to use infrequently, whenever we need to update stores data
    """
    Stores.objects.all().delete()

    j = json.load(open(filepath 'r'))
    for store in j:
        s = Stores.objects.get_or_create(store_id=store['id'],
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
