#!usr/bin/env python

import requests
import lxml.html
from lxml.cssselect import CSSSelector
import json


def open_url(url):
    '''
    collects our response object
    '''
    r = requests.get(url)
    if r.status_code == 200:
        return r.text # r.content if we need binary
    else:
        raise Exception('You are an idiot. Bad link.')


def parse_html(unparsed_html):
    '''
    the initial parse of the html
    '''
    return lxml.html.fromstring(unparsed_html)


def treeify(url):
    '''
    gets the parsed tree to begin the scrape
    '''
    unparsed_html = open_url(url)
    return parse_html(unparsed_html)


def how_many_stores(tree):
    '''
    not strictly necessary, but it will give us a value to check our
    data-container counts against if we need it plus a little quick output
    '''
    num_stores_selector = CSSSelector('span.collectionText_SL')
    print num_stores_selector(tree)[0].text


def get_retail_ids(tree):
    '''
    each PLCB retail location has a unique store number
    '''
    print "collecting IDs like a bouncer ..."
    store_id_selectors = CSSSelector('span.boldMaroonText')
    store_ids = store_id_selectors(tree)
    return [store_id.text.strip() for store_id in store_ids]


def get_store_types(tree):
    print "finding store types ...."
    store_type_selectors = CSSSelector('div#storetype.columnTypeOfStore')
    store_type_elements = store_type_selectors(tree)
    return [store_type.text.strip() for store_type in store_type_elements]


def get_retail_hours(tree):
    '''
    hours of operation come off the page a little funky, so days and hours
    need to be collected together, then turned into full weeks
    '''
    print "getting hours ...."
    # grabbing days and hours separately
    retail_store_days_selectors = CSSSelector('div.weekDayParent')
    retail_store_hours_selectors = CSSSelector('div.timeSpanParent')
    # pairing DOM elements containing days and hours
    retail_store_hours_elements = zip(retail_store_days_selectors(tree), retail_store_hours_selectors(tree))
    # unpacking elements
    retail_store_hours = [(day.text, hours_range.text) for (day, hours_range) in retail_store_hours_elements]
    # chunking (days, hours) tuples out into weeks
    return [retail_store_hours[x:x + 7] for x in xrange(0, len(retail_store_hours), 7)]


def unpack_lat_long_address_phone(tree):
    '''
    the cleanest place on the page to collect these and separate them
    into their own lists
    '''
    print "demystifying store location data ...."
    inputs = CSSSelector('.columnDistance form input')(tree)
    Entry = collections.namedtuple('Entry', 'longitude latitude address phone')
    longitude_offset = 0
    latitude_offset = 1
    address_offset = 2
    phone_offset = 3
    input_field_count = 5
    entries = [
        Entry(longitude=inputs[n + longitude_offset].value,
              latitude=inputs[n + latitude_offset].value,
              address=inputs[n + address_offset].value,
              phone=inputs[n + phone_offset].value)
        for n in range(0, len(inputs), input_field_count]
    return ([e.longitude for e in entries],
            [e.latitude for e in entries],
            [e.address for e in entries],
            [e.phone for e in entries])


def dict_builder(url):
    '''
    assembles our objects into serializable form
    '''
    tree = treeify(url)
    # will give us a quick output string, just so we have an idea we've
    # hit the right thing
    how_many_stores(tree)

    retail_store_ids = get_retail_ids(tree)
    hours = get_retail_hours(tree)
    store_types = get_store_types(tree)
    longitudes, latitudes, addresses, phone_numbers = unpack_lat_long_address_phone(tree)

    print "building JSON-able data sets ...."
    # creates dictionaries for serializing into json
    return [{"id": store,
             "hours": hours[i],
             "longitude": longitudes[i],
             "latitude": latitudes[i],
             "address": addresses[i],
             "phone": phone_numbers[i],
             "store_type": store_types[i] if len(store_types[i]) > 1 else "Regular-ass store"} for i, store in enumerate(retail_store_ids)]


def write_json_to_file(data):
    '''
    stores our objects in a pprint format
    '''
    print 'writing json ....'
    j = json.dumps(data, indent=4)
    with open('retail_location_data.json', 'w') as f:
        print >> f, j


def start_scrape():
    '''
    runs the main functions to do the damn thang
    '''
    data = dict_builder('http://www.finewineandgoodspirits.com/webapp/wcs/stores/servlet/FindStoreView?storeId=10051&langId=-1&catalogId=10051&pageNum=1&listSize=700&category=&city=&zip_code=&county=All+Stores&storeNO=%')
    write_json_to_file(data)
    print "done."


start_scrape()
