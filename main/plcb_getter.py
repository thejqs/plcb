#!usr/bin/env python

import requests
from lxml import etree
import StringIO
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


def parse_html(html):
    '''
    the initial parse of the html
    '''
    parser = etree.HTMLParser()
    return etree.parse(StringIO.StringIO(html), parser)


def treeify(url):
    '''
    gets the parsed tree to begin the scrape
    '''
    html = open_url(url)
    return parse_html(html)


def get_retail_ids(tree):
    '''
    each PLCB retail location has a unique store number
    '''
    print "collecting IDs like a bouncer ..."
    return [num.strip() for num in tree.xpath('/html/body/div[1]/div/div[3]/div[4]/div/div[2]/span[2]/text()')]


def get_retail_hours(tree):
    '''
    hours of operation come off the page a little funky, so days and hours
    need to be collected, then turned into full weeks
    '''
    print "getting hours ...."
    retail_store_hours = tree.xpath('/html/body/div[1]/div/div[3]/div[4]/div/div[4]/div/div/text()')
    # makes one big list of tuples of (day_of_week, hours_of_operation)
    hours_tuples = zip(retail_store_hours, retail_store_hours[1::])[::2]
    # chunks hours_tuples out into lists of tuples, each representing a week
    # and the regular hours of each store
    return [hours_tuples[x:x + 7] for x in xrange(0, len(hours_tuples), 7)]


def assemble_lat_long_address_phone(tree):
    '''
    the cleanest place on the page to collect these, though we'll need to break
    them apart in short order to use them differently
    '''
    print "demystifying store location data ...."
    # ignoring a duplicate value with extra html tags
    return [option.values()[2] for option in tree.xpath('/html/body/div[1]/div/div[3]/div[4]/div/div[5]/form/input') if '<br>' not in option.values()[2]]


def get_lat_long(retail_store_data):
    '''
    makes sure we store these somewhere predictable for
    later mapping, both to an object and to a, um, map
    '''
    # we'll use latitude and longitude together, and differently than address and phone. so let's chunk those out into usable storage.
    return [tuple(retail_store_data[x:x + 2]) for x in xrange(0, len(retail_store_data), 4)]


def get_address_phone(retail_store_data):
    '''
    stores these together for later display in predictable order
    '''
    return [tuple(retail_store_data[x:x + 2]) for x in xrange(2, len(retail_store_data), 4)]


def dict_builder(url):
    '''
    assembles our objects into serializable form
    '''
    tree = treeify(url)
    # will give us an output string, just so we have an idea we've
    # hit the right thing
    num_stores_xpath = '/html/body/div[1]/div/div[3]/div[4]/div[5]/div/span/text()'
    print tree.xpath(num_stores_xpath)

    retail_store_ids = get_retail_ids(tree)
    hours = get_retail_hours(tree)
    retail_store_data = assemble_lat_long_address_phone(tree)
    lat_long = get_lat_long(retail_store_data)
    address_phone = get_address_phone(retail_store_data)

    print "building serializable data sets ...."
    # creates a list of dictionaries for serializing into json
    return [{"id": store, "hours": hours[i], "latitude": float(lat_long[i][0]), "longitude": float(lat_long[i][1]), "address": address_phone[i][0], "phone": address_phone[i][1]} for i, store in enumerate(retail_store_ids)]

    # print "finding store types ...."
    # need to investigate why this is giving me a weird number of values --
    # I'll want this, but not worth slowing down working on everything else.
    # they're mostly blank, but we should ID premium collection stores
    # retail_store_type_list = [elem.strip() for elem in tree.xpath('/html/body/div[1]/div/div[3]/div[4]/div/div[3]/text()')]

    # print "there are", len(retail_store_type_list), "things in the type_list"


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
    runs the functions to do the damn thang
    '''
    data = dict_builder('http://www.finewineandgoodspirits.com/webapp/wcs/stores/servlet/FindStoreView?storeId=10051&langId=-1&catalogId=10051&pageNum=1&listSize=700&category=&city=&zip_code=&county=All+Stores&storeNO=%')
    write_json_to_file(data)
    print "done."


start_scrape()
