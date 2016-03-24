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
        return r.text  # r.content if we need binary
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
    store_ids_elements = CSSSelector('span.boldMaroonText')(tree)
    return [store_id.text.strip() for store_id in store_ids_elements]


def get_store_types(tree):
    print "finding store types ...."
    store_type_elements = CSSSelector('div#storetype.columnTypeOfStore')(tree)
    return [store_type.text.strip() for store_type in store_type_elements]


def get_retail_hours(tree):
    '''
    hours of operation come off the page a little funky, so days and hours
    need to be collected together, then turned into full weeks
    '''
    print "getting hours ...."
    # grabbing days and hours separately
    retail_store_days_elements = CSSSelector('div.weekDayParent')(tree)
    retail_store_hours_elements = CSSSelector('div.timeSpanParent')(tree)
    # pairing DOM elements containing days and hours
    retail_store_hours_zipped = zip(retail_store_days_elements,
                                    retail_store_hours_elements)
    # unpacking elements
    retail_store_hours = [(day.text, hours_range.text)
                          for (day, hours_range) in retail_store_hours_zipped]
    # chunking (days, hours) tuples out into weeks
    weeks_offset = 7
    return [retail_store_hours[x:x + weeks_offset]
            for x in xrange(0, len(retail_store_hours), weeks_offset)]


def unpack_lat_long_address_phone(tree):
    '''
    a hidden form element is the cleanest place on the page to collect these.
    they come off together, so we need to format and separate them
    into their own lists.
    comes in as:
    [0]longitude
    [1]latitude
    [2]address
    [3]phone
    [4]duplicate (and messy) address field, which we don't need
    repeat
    '''
    print "demystifying store location data ...."
    elements = CSSSelector('.columnDistance form input')(tree)
    # lat_long_address_phone_elements = lat_long_address_phone_selectors(tree)
    longitude_offset = 0
    latitude_offset = 1
    address_offset = 2
    phone_offset = 3
    len_input_fields = 5

    longitudes = [float(elements[x].value)
                  for x in xrange(longitude_offset, len(elements), len_input_fields)]
    latitudes = [float(elements[x].value)
                 for x in xrange(latitude_offset, len(elements), len_input_fields)]
    addresses = [elements[x].value
                 for x in xrange(address_offset, len(elements), len_input_fields)]
    phone_numbers = [elements[x].value
                     for x in xrange(phone_offset, len(elements), len_input_fields)]

    return longitudes, latitudes, addresses, phone_numbers


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

    longitudes,
    latitudes,
    addresses,
    phone_numbers = unpack_lat_long_address_phone(tree)

    print "building JSON-able data sets ...."
    # creates dictionaries for serializing into json
    return [{"id": store,
             "hours": hours[i],
             "longitude": longitudes[i],
             "latitude": latitudes[i],
             "address": addresses[i],
             "phone": phone_numbers[i],
             "store_type": store_types[i] if len(store_types[i]) > 1
             else "Regular-ass store"}
            for i, store in enumerate(retail_store_ids)]


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
    # a note about the URL: the site supports my manually adding a large(r)
    # number to the listSize attribute here even though it's not a page option.
    # the call to .format() is simply to make that more explicit
    # for future me or anyone who has to read this
    data = dict_builder('http://www.finewineandgoodspirits.com/webapp/wcs/stores/servlet/FindStoreView?storeId=10051&langId=-1&catalogId=10051&pageNum=1&listSize={0}&category=&city=&zip_code=&county=All+Stores&storeNO=%'.format(700))
    write_json_to_file(data)
    print "done."


start_scrape()
