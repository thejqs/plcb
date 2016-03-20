#!usr/bin/env python

import collections
import requests
from lxml import etree
import StringIO
import csv
import json


def open_url(url):
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


def dict_builder(url):
    tree = treeify(url)

    # will store data about each PLCB retail location; store_id as key
    # stores = []
    # will give us a string, just so we have an idea we've hit the right thing
    num_stores_xpath = '/html/body/div[1]/div/div[3]/div[4]/div[5]/div/span/text()'
    print tree.xpath(num_stores_xpath)

    print "collecting IDs like a bouncer ..."
    retail_store_ids = [num.strip() for num in tree.xpath('/html/body/div[1]/div/div[3]/div[4]/div/div[2]/span[2]/text()')]

    print "getting hours ...."
    retail_store_hours = tree.xpath('/html/body/div[1]/div/div[3]/div[4]/div/div[4]/div/div/text()')
    # makes one big list of tuples of (day_of_week, hours_of_operation)
    hours_tuples = zip(retail_store_hours, retail_store_hours[1::])[::2]
    # chunks hours_tuples out into lists of tuples, each representing a week
    # and the regular hours of each store
    hours_sets = [hours_tuples[x:x + 7] for x in xrange(0, len(hours_tuples), 7)]

    # print "finding store types ...."
    # need to investigate why this is giving me a weird number of values --
    # I'll want this, but not worth slowing down everything.
    # they're mostly blank, but we should ID premium collection stores
    # retail_store_type_list = [elem.strip() for elem in tree.xpath('/html/body/div[1]/div/div[3]/div[4]/div/div[3]/text()')]

    # print "there are", len(retail_store_type_list), "things in the type_list"

    print "demystifying store location data ...."
    retail_store_data = [option.values()[2] for option in tree.xpath('/html/body/div[1]/div/div[3]/div[4]/div/div[5]/form/input') if '<br>' not in option.values()[2]]

    # we'll use latitude and longitude together, and differently than address and phone. so let's chunk those out into usable storage.
    lat_long = [tuple(retail_store_data[x:x + 2]) for x in xrange(0, len(retail_store_data), 4)]

    address_phone = [tuple(retail_store_data[x:x + 2]) for x in xrange(2, len(retail_store_data), 4)]
    # this will chunk it out into lists of lists, each containing
    # one discrete set of long, lat, address, phone
    # retail_store_data_final = [retail_store_data[x:x + 4] for x in xrange(0, len(retail_store_data), 4)]

    print "building data sets ...."
    # creates a list of dictionaries for serializing into json
    data = [{"id": store, "hours": hours_sets[i], "latitude": float(lat_long[i][0]), "longitude": float(lat_long[i][1]), "address": address_phone[i][0], "phone": address_phone[i][1]} for i, store in enumerate(retail_store_ids)]

    print 'writing json'
    j = json.dumps(data, indent=4)
    with open('retail_location_data.json', 'w') as f:
        print >> f, j

    # print 'writing csv'
    # writer = csv.writer(open('retail_data.csv', 'wb'))
    # writer.writerow(data)

    print "done."

    return data


# def start_scrape():
#     '''
#     runs the functions to do the damn thang
#     '''
dict_builder('http://www.finewineandgoodspirits.com/webapp/wcs/stores/servlet/FindStoreView?storeId=10051&langId=-1&catalogId=10051&pageNum=1&listSize=700&category=&city=&zip_code=&county=All+Stores&storeNO=%')
