import requests
from lxml import etree
import StringIO


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
    parse_html(html)


def dict_builder(url):
    tree = treeify(url)

    # will store data about each PLCB retail location; store_id as key
    stores = {}
    # will give us a string, just so we have an idea we've hit the right thing
    num_stores_xpath = '/html/body/div[1]/div/div[3]/div[4]/div[5]/div/span/text()'
    print tree.xpath(num_stores_xpath)

    print "collecting IDs like a bouncer ..."
    retail_store_ids = [num.strip() for num in tree.xpath('/html/body/div[1]/div/div[3]/div[4]/div/div[2]/span[2]/text()')]

    print "getting hours ...."
    retail_store_hours = tree.xpath('/html/body/div[1]/div/div[3]/div[4]/div/div[4]/div/div/text()')
    # makes a list of tuples of (day_of_week, hours_of_operation)
    # with Sunday at position[0]
    hours_tuples = zip(retail_store_hours, retail_store_hours[1::])[::2]

    # print "finding store types ...."
    # need to investigate why this is giving me a weird number of values --
    # I'll want this, but not worth slowing down everything.
    # they're mostly blank, but we should ID premium collection stores
    # retail_store_type_list = [elem.strip() for elem in tree.xpath('/html/body/div[1]/div/div[3]/div[4]/div/div[3]/text()')]

    # print "there are", len(retail_store_type_list), "things in the type_list"

    print "demystifying store location data ...."
    retail_store_data = [option.values()[2] for option in tree.xpath('/html/body/div[1]/div/div[3]/div[4]/div/div[5]/form/input') if '<br>' not in option.values()[2]]
    # this will chunk it out into lists of lists, each containing
    # one discrete set of long, lat, address, phone
    # retail_store_data_final = [retail_store_data[x:x + 4] for x in xrange(0, len(retail_store_data), 4)]

    print "building dict ...."
    # resulting dict has retail hours by (day_of_week, hours) in tuples
    # at indices 0-6, longitude at 7, latitude at 8, address at 9, phone at 10
    # and unique store ids in strings as keys
    for i, store in enumerate(retail_store_ids):
        days = 7
        len_location_data = 4
        stores[store] = hours_tuples[:days]
        # busting these out of list form; we'll need to use them differently
        for data in retail_store_data[:len_location_data]:
            stores[store].append(data)
        del hours_tuples[:days]
        del retail_store_data[:len_location_data]

    print stores
    return stores


def start_scrape():
    '''
    runs the functions to do the damn thang
    '''
    dict_builder(url)
