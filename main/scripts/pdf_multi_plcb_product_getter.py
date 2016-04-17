#!usr/bin/env python

'''
A crawler to search every product in the
Pennsylvania Liquor Control Board's database, searching for unicorns:
products available for sale in only one retail store in the entire state.

Configured to use Python's multiprocessing module -- thus I can't use
generators everywhere I'd like. Life is just hard sometimes. Boo. Also hoo.

The PLCB claims the database is updated at the close of business every day,
but it's more like 5 or 7 a.m. the following day at the earliest. Nonetheless,
that's still before stores open for the day.

Every day is a chance for fresh data.

This script parses a PDF of the PLCB database published every day about 8 a.m.
in order to collect product ids needed to run the main scraper.
Doing it that way saves us about 2,400 get requests a day to a brittle
search site which doesn't take too many requests for it to get unreliable.
Also saves about two hours of runtime. So, y'know, that's good.

On any given day, there are about 14,000 or so products in PLCB stores.
Those we can test for unicorns, which usually number about 2,000.
Total time: about an hour and 15 minutes.

Fun, right?
'''

import requests
import lxml.html
from lxml.cssselect import CSSSelector
import json
import datetime
import re
from multiprocessing import Pool

import pdf_parser


def open_url(url):
    '''
    collects a response object

    Returns:
    a raw string of html
    '''
    try:
        headers = {'user-agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.8 // Jacob Quinn Sanders, War Streets Media/jacob@warstreetsmedia.com"}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return r.text
        else:
            print 'You got a {0} error from {1}'.format(r.status_code, r.url)
            raise Exception('You are an idiot. Bad link.')
    except requests.exceptions.ConnectionError as e:
        print datetime.datetime.now()
        print e
        print url
        print 'no delicious bytes to eat getting {0}'.format(url)


def parse_html(unparsed_html):
    '''
    an initial parse of raw html

    Returns:
    a DOM tree
    '''
    try:
        return lxml.html.fromstring(unparsed_html)
    except TypeError as e:
        print '{0}\n{1}\n{2}\n'.format(datetime.datetime.now(), e, unparsed_html)


def treeify(url):
    '''
    where possible, a function to run the getting and the DOM-treeing together
    '''
    unparsed_html = open_url(url)
    return parse_html(unparsed_html)


def write_unicorn_json_to_file(data):
    '''
    stores our assembled dicts as JSON objects in a pprint format

    Args:
    any serializable data structure, really, but in our case
    a dictionary or list of dictionaries
    '''
    j = json.dumps(data, sort_keys=True, indent=4)
    with open('../data/unicorns_json/unicorns-{}.json'.format(datetime.date.today()), 'a+') as f:
        print >> f, j


def make_product_urls(codes):
    '''
    Args:
    a list of all product ids, usually between 14,000 and 16,000
    '''
    product_urls = []
    for code in codes:
        product_url = 'http://www.lcbapps.lcb.state.pa.us/webapp/product_management/psi_ProductInventory_Inter.asp?cdeNo={0}'.format(code)
        product_urls.append(product_url)
    return product_urls


def check_for_unicorn(tree):
    '''
    gives us a quick thumbs-up or thumbs-down on whether each product page
    contains a unicorn.

    Args:
    the parsed DOM tree of a product page
    '''
    check_unicorn = CSSSelector('body table tr td table tr td font')(tree)
    is_unicorn = False
    try:
        if 'one Location' in check_unicorn[0].text:
            is_unicorn = True
        return is_unicorn
    except IndexError:
        print 'no text to check here. weird.'
        print tree
        return 'this one needs to be checked'


def assemble_unicorn(tree):
    '''
    if a product passes the unicorn test, this gets called to assemble
    our main unicorn object.

    Args:
    the parsed DOM tree of a unicorn product page

    Returns:
    a dict of most of our object -- a unicorn dict, if you will
    '''
    unicorn_store_elements = CSSSelector('tr td.table-data')(tree)
    unicorn_store = [i.text.strip() for i in unicorn_store_elements]

    try:
        # this next bit only breaks if the target data is being updated and
        # changed on the server end or we have a bad DOM tree --
        # which are good times to break
        unicorn_store_id = unicorn_store[0]
        # there can be as many as three digits at the beginning of each
        # number-of-units string for sure and theoretically more.
        # hence the regex to handle the variations in number of digits.
        # preceded by the .replace() on the off-chance inventory is >1000
        # as strings of four-digit numbers on this site all carry commas
        num_unicorn_bottles = unicorn_store[2].replace(',', '')
        # perhaps a little overwrought -- \d+ would accomplish much the same --
        # but just being careful
        num_unicorn_bottles_pattern = '(^\d+(?!\S))'
        num_unicorn_bottles = re.match(num_unicorn_bottles_pattern, num_unicorn_bottles).group()

        unicorn_product_elements = CSSSelector('ul li.newsFont b')(tree)
        unicorn_product = [i.text.strip() for i in unicorn_product_elements]
        unicorn_code = unicorn_product[0]
        unicorn_name = unicorn_product[1]
        unicorn_bottle_size = unicorn_product[2]
        # prices over $1000 -- there are a few -- have a comma in them
        unicorn_price = unicorn_product[3][1:].replace(',', '')

        # need a mutable data structure here to extend by assignment later
        return {'store_id': unicorn_store_id,
                # handling a case where some names have extra spaces not caught
                # by the earlier .strip()
                'name': unicorn_name.replace('  ', ''),
                # we'll want these two de-stringified for value comparisons:
                'price': float(unicorn_price),
                'bottles': int(num_unicorn_bottles),
                'product_code': unicorn_code,
                'bottle_size': unicorn_bottle_size,
                'scrape_date': '{0}'.format(datetime.date.today())}

    except IndexError as e:
        print '{0}\n{1}\n'.format(e, unicorn_store)
        raise Exception('looks like time for a server update or a bad URL. breathe. we can try again.')


def on_sale(tree):
    '''
    a separate element, when present. this could change, even if the unicorn
    remains a unicorn. and if we're collecting price, it would be incomplete
    of us not to check this

    Returns:
    whether each unicorn item was on sale for addition to each unicorn dict
    '''
    sale_element = CSSSelector('ul li.newsFont b font')(tree)
    if len(sale_element) > 0:
        return sale_element[0].text
    else:
        return False


def unicorn_scrape(trees):
    '''
    collects product data if the product passes the unicorn test.

    Args:
    a list of product-page DOM tree

    Returns:
    a list of unicorn dicts, each of which contains a unicorn
    '''
    unicorns = []
    for tree in trees:
        is_unicorn = check_for_unicorn(tree)
        # just being explicit about our False case
        if not is_unicorn:
            continue
        else:
            unicorn = assemble_unicorn(tree)
            sale_price = on_sale(tree)
            # it's either this or a ternary operator, so ....
            try:
                unicorn['on_sale'] = float(sale_price.replace('Sale Price: $', ''))
            except (ValueError, AttributeError) as e:
                unicorn['on_sale'] = False
            unicorns.append(unicorn)
    print 'found {0} unicorns ....'.format(len(unicorns))
    return unicorns


def hunt_unicorns():
    '''
    once our product ids are in hand, we can search each product page
    in earnest to ask it whether it is that rarest of beasts

    Args:
    if using: a url on which to begin running these functions.
    if product codes are already in hand -- stashed in a text file, say --
    can run based on those with no args

    Returns:
    a JSON-serializable list of unicorn dicts
    '''
    start_products = datetime.datetime.now()
    print start_products

    all_product_codes = pdf_parser.collect()

    end_products = datetime.datetime.now()
    print end_products - start_products

    # should things fall apart after this point, can simply read in the product codes from a file:
    # for yesterday: datetime.date.today() - datetime.timedelta(days=1)
    # with open('../data/product_codes/product_codes-{}.txt'.format(datetime.date.today()), 'r') as f:
        # all_product_codes = [line.strip() for line in f]
    product_urls = make_product_urls(all_product_codes)
    print 'made {0} urls ....'.format(len(product_urls))
    print 'getting product urls ....'
    # multiprocessing module can't handle lxml DOM tree elements, apparently.
    # so granularly we go
    rs = (u for u in p.imap_unordered(open_url, product_urls))
    print 'making DOM trees ... happy little DOM trees ....'
    trees = (parse_html(r) for r in rs)
    print 'hunting unicorns ....'
    unicorns = unicorn_scrape(trees)

    print 'writing unicorns to json ....'
    write_unicorn_json_to_file(unicorns)
    print 'done hunting.'

    end_unicorns = datetime.datetime.now()
    print end_unicorns - start_products
    print 'all cleaned up. long day. tacos?'


if __name__ == '__main__':
    p = Pool(8)
    hunt_unicorns()
