#!usr/bin/env python

import django
import os, sys

sys.path.append("../..")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

import requests
from lxml import etree
import StringIO
import json
import datetime
from main.models import Store, Unicorn
from project.settings_local import geojson_key
django.setup()


def get_store_tree(unicorn):
    '''
    given a unicorn from our scraper JSON, uses its product code
    to find out missing store

    returns:
    a parsed DOM tree
    '''
    r = requests.get('https://www.lcbapps.lcb.state.pa.us/webapp/Product_Management/psi_ProductInventory_Inter.asp?cdeNo={}'.format(unicorn['product_code']))
    parser = etree.HTMLParser()
    return etree.parse(StringIO.StringIO(r.text), parser)


def format_hours(hours):
    '''
    args:
    an alternating list of days and ranges of hours as strings

    returns:
    a list of tuples with days and hours expressly linked
    '''
    hours_days = hours[::2]
    hours_range = hours[1::2]
    return zip(hours_days, hours_range)


def get_lat_long(address):
    '''
    leverages Google's realtime address-conversion API to extract latitude and
    longitude for our new Store object

    args:
    an address string to pass to the API
    '''
    p = {'address': address, 'key': geojson_key}
    r = requests.get('https://maps.googleapis.com/maps/api/geocode/json?', params=p)
    latitude = r.json()['results'][0]['geometry']['location']['lat']
    longitude = r.json()['results'][0]['geometry']['location']['lng']
    return latitude, longitude


def make_new_store(unicorn):
    '''
    sometimes the PLCB adds inventory for a new store before it opens. we still
    want to capture that. in case of a store_id not in our database, we'll
    create the object as a last resort if we don't have it

    args:
    unicorn JSON to hand off to the Store-building function

    returns:
    a Store object
    '''
    store = Store()
    tree = get_store_tree(unicorn)
    store_type = tree.xpath('//*/table[3]/tr[4]/*/font/text()')
    hours = [s.strip() for s in tree.xpath('/html/body/table[3]/tr[4]/td[3]/table/tr/td/font/text()')]
    address_and_phone = [s.strip() for s in tree.xpath('//*/table[3]/tr[4]/td[2]/text()')]
    store.store_id = tree.xpath('//*/tr[4]/td/text()')[0].strip()

    address = ''
    for entry in address_and_phone:
        if 'Fax' in entry or entry is None:
            continue
        if 'Phone' in entry:
            store.phone = entry.replace('Phone: ', '').replace('-', '.')
        else:
            entry += ' '
            address += entry
            print address
        address = address.strip()
        print address
        store.address = address

    store.latitude, store.longitude = get_lat_long(address)
    if store_type and 'Premium' in store_type[1]:
        store.store_type = [s.strip() for s in store_type][1][:-6]
    else:
        store.store_type = 'Regular-ass store'
    store.hours = [{day: hours_range} for (day, hours_range) in format_hours(hours)]
    store_data_date = datetime.date.today().strftime('%Y-%m-%d')
    store.save()


def import_unicorns(filepath):
    '''
    called from pdf_multi_plcb_product_getter.py

    given our daily scraped data, passes it into our
    PostgreSQL time-series table
    '''
    j = json.load(open(filepath, 'r'))
    for unicorn in j:
        u = Unicorn()
        u.product_id = unicorn['product_code']
        u.name = unicorn['name']
        u.num_bottles = unicorn['bottles']
        u.bottle_size = unicorn['bottle_size']
        u.price = unicorn['price']
        u.on_sale = unicorn['on_sale']
        u.on_sale_price = unicorn['on_sale']
        u.scrape_date = unicorn['scrape_date']
        # this is super ugly. for now it just needs to work
        try:
            u.store = Store.objects.get(store_id=str(unicorn['store_id']),
                                        store_data_date='2016-04-10')
        except Store.DoesNotExist:
            try:
                u.store = Store.objects.get(store_id=str(unicorn['store_id']),
                                            store_data_date='2016-05-15')
            except Store.DoesNotExist:
                try:
                    u.store = Store.objects.get(store_id=str(unicorn['store_id']),
                                                store_data_date__gt='2016-05-15')
                except Store.DoesNotExist:
                    print 'making a new store ....'
                    make_new_store(unicorn)
                    u.store = Store.objects.get(store_id=unicorn['store_id'],
                                                store_data_date=datetime.date.today().strftime('%Y-%m-%d'))

        u.save()


# def import_stores(filepath):
#     '''
#     a function to use infrequently, whenever we need to update stores data
#     '''
#     Store.objects.all().delete()
#
#     j = json.load(open(filepath, 'r'))
#     for store in j:
#         s = Store.objects.get_or_create(store_id=store['id'],
#                                         address=store['address'],
#                                         hours=store['hours'],
#                                         latitude=store['latitude'],
#                                         longitude=store['longitude'],
#                                         phone=store['phone'],
#                                         store_type=store['store_type'])


def migrate():
    # import_stores()
    import_unicorns()


if __name__ == '__main__':
    import_unicorns()
