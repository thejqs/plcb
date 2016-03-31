#!usr/bin/env python

'''
A synchronous crawler to search every product in the
Pennsylvania Liquor Control Board's database, searching for unicorns:
products available for sale in only one retail store in the entire state.
It takes a really, really, really long time to run.

The PLCB claims the database is updated at the close of business every day,
but it's more like 5 a.m. the following day. Nonetheless, that's still before
stores open for the day. Every day is a chance for fresh data.

On any given day, given the structure of the PLCB's
product search interfaces, we have about 2,400 pages to crawl
to wade through about 60,000 products to see the 13,000 or 14,000
which are in stores, and then we can test for unicorns,
which usually number about 2,000.

Fun, right?
'''

import requests
import lxml.html
from lxml.cssselect import CSSSelector
import json
import datetime
import re


def open_url(url):
    '''
    collects our response object
    '''
    headers = {'user-agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 // Jacob Quinn Sanders, War Streets Media: jacob@warstreetsmedia.com"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.text
    else:
        print 'You got a {0} error from {1}'.format(r.status_code, r.url)
        raise Exception('You are an idiot. Bad link.')


def parse_html(unparsed_html):
    '''
    the initial parse of the html
    '''
    return lxml.html.fromstring(unparsed_html)


def treeify(url):
    '''
    returns the parsed html tree to begin the scrape
    '''
    unparsed_html = open_url(url)
    return parse_html(unparsed_html)


def write_unicorn_json_to_file(data):
    '''
    stores our objects in a pprint format
    '''
    print 'writing json ....'
    j = json.dumps(data, sort_keys=True, indent=4)
    with open('unicorns-{}.json'.format(datetime.date.today()), 'a') as f:
        print >> f, j


def write_codes_to_file(data):
    with open('product_codes-{}.txt'.format(datetime.date.today()), 'a') as f:
        print >> f, data


def get_total_numbers(tree):
    '''
    collects the total number of pages and products we have to crawl.
    they come in as strings with extra words and a comma we have to handle
    '''
    nums = CSSSelector('form table tr td')(tree)
    num_pages = int(''.join(n for n in nums[0].text[10:].split(',')))
    num_products = int(''.join(n for n in nums[1].text[25:].split(',')))
    return (num_pages, num_products)


def get_product_codes(tree):
    '''
    collects the product codes that will complete our product-page URLs
    so we can check each for unicorns
    '''
    codes_elements = CSSSelector('td a b font')(tree)
    return [code.text for code in codes_elements if code.text.isdigit()]


def make_search_urls(pages):
    '''
    a generator to help us iterate through the main search pages one at a time.
    the number series the URL structure supports begins with the numeral 2

    Args:
    the total number of pages to search
    '''
    # We've already captured data from one -- our initial -- URL by this point
    for page in xrange(2, pages + 1):
        search_url = 'https://www.lcbapps.lcb.state.pa.us/webapp/Product_Management/psi_ProductListPage_Inter.asp?strPageNum={0}&selTyp=&selTypS=&selTypW=&selTypA=&searchCode=&searchPhrase=&CostRange=&selSale=&strFilter=&prevSortby=BrndNme&sortBy=BrndNme&sortDir=ASC'.format(page)
        yield search_url


def make_product_urls(all_product_codes):
    '''
    a generator to hand off each product-page URL as it gets built

    Args:
    all product ids as generator elements
    '''
    for code in all_product_codes:
        product_url = 'http://www.lcbapps.lcb.state.pa.us/webapp/product_management/psi_ProductInventory_Inter.asp?cdeNo={0}'.format(code)
        yield product_url


def parse_search_page(pages):
    '''
    pulls product codes matching our needs from each search page

    Args:
    the number of total pages to search for product ids
    '''
    codes = []
    for i, search_url in enumerate(make_search_urls(pages)):
        search_tree = treeify(search_url)
        new_codes = get_product_codes(search_tree)
        codes += new_codes
        # writing these to a file in case our script breaks --
        # wouldn't want to have to re-run the whole thing
        for code in new_codes:
            write_codes_to_file(code)
        print 'collected {0} total new codes from {1} pages'.format(len(codes), i + 2)
    return codes


def check_for_unicorn(tree):
    '''
    gives us a quick thumbs-up or thumbs-down on whether each product page
    contains a unicorn

    Args:
    the parsed tree element of a product page
    '''
    check_unicorn = CSSSelector('body table tr td table tr td font')(tree)
    is_unicorn = False
    if ' one ' in check_unicorn[0].text:
        is_unicorn = True
    return is_unicorn


def assemble_unicorn(tree):
    '''
    if a product passes the unicorn test, this gets called to assemble
    our main unicorn object.

    Args:
    the parsed tree element of a product page

    Returns:
    a dict of our object -- a unicorn dict, if you will
    '''
    unicorn_store_elements = CSSSelector('tr td.table-data')(tree)
    unicorn_store = [i.text.strip() for i in unicorn_store_elements]
    unicorn_store_id = unicorn_store[0]
    # there can be as many as three digits at the beginning of each
    # number-of-units string for sure and theoretically more,
    # followed by a space: 'x units'
    # hence this regex to handle the string variations
    num_unicorn_bottles_pattern = '(^\d+(?!\S))'
    num_unicorn_bottles = re.match(num_unicorn_bottles_pattern, unicorn_store[2]).group()

    # would wrap this in a try-except but it only breaks if the target
    # data is being updated -- which is a good time to break
    unicorn_product_elements = CSSSelector('ul li.newsFont b')(tree)
    unicorn_product = [i.text.strip() for i in unicorn_product_elements]
    unicorn_code = unicorn_product[0]
    unicorn_name = unicorn_product[1]
    unicorn_bottle_size = unicorn_product[2]
    # prices over $1000 -- and there are at least a few -- carry a comma
    unicorn_price = unicorn_product[3][1:].replace(',', '')

    # need a mutable data structure here to extend by assignment later
    return {'store_id': unicorn_store_id,
            # handling a case where some names have extra spaces not caught
            # by the earlier .strip()
            'name': unicorn_name.replace('  ', ' '),
            # we'll want these two de-stringified for value comparisons:
            'price': float(unicorn_price),
            'bottles': int(num_unicorn_bottles),
            'product_code': unicorn_code,
            'bottle_size': unicorn_bottle_size,
            'scrape_date': datetime.date.today()}


def on_sale(tree):
    '''
    a separate element, when present. this data gets updated daily,
    so could change. and if we're collecting price, it would be incomplete
    of us not to check this

    Args:
    the parsed tree element of a product page

    Returns:
    if on sale: a string containing the sale price
    '''
    sale_element = CSSSelector('ul li.newsFont b font')(tree)
    if len(sale_element) > 0:
        return sale_element[0].text
    else:
        return False


def unicorn_scrape(product_urls):
    '''
    collects product data if the product passes the unicorn test

    Args:
    all of the product URLs to which we will apply the unicorn test,
    gathering data if it passes

    Returns:
    a list of dicts, each of which contains a unicorn
    '''
    unicorns = []
    for i, product_url in enumerate(product_urls):
        product_tree = treeify(product_url)
        print "{0} searching ....".format(i)
        is_unicorn = check_for_unicorn(product_tree)
        if not is_unicorn:
            continue
        else:
            unicorn = assemble_unicorn(product_tree)
            sale_price = on_sale(product_tree)
            # it's either this or a ternary operator, so ....
            try:
                unicorn['on_sale'] = float(sale_price.replace('Sale Price: $', ''))
            except (ValueError, AttributeError) as e:
                unicorn['on_sale'] = False
            # .append() because it expects an object
            unicorns.append(unicorn)
            print 'FOUND A UNICORN:', unicorn

    print 'here you go: {0} unicorns'.format(len(unicorns))
    return unicorns


def prepare_unicorn_search(url):
    '''
    assembles everything we need to perform the search,
    getting the heavy lifting of walking all the search pages
    out of the way so we can focus on what we care about.

    Returns:
    a list of product ids we need to append to a URL stub

    Note:
    when the search-page server goes down, the product pages stay up.
    so for now, makes sense to traverse the search pages first
    to collect the ids we need in case anything happens to those servers
    while we're searching products
    '''
    tree = treeify(url)
    pages, products = get_total_numbers(tree)
    print 'searching {0} pages and {1} products for unicorns ....'.format(pages, products)
    page_product_codes = get_product_codes(tree)
    # whatever product ids we find on the first search page:
    for code in page_product_codes:
        write_codes_to_file(code)
    print 'found {0} initial product codes'.format(len(page_product_codes))
    page_product_codes += parse_search_page(pages)
    return page_product_codes


def hunt_unicorns(url=None):
    '''
    once our product ids are in hand, we can search each product page
    in earnest to ask it whether it is that rarest of beasts

    Args:
    a url on which to begin running these functions

    Returns:
    a JSON-serializable list of unicorn dicts
    '''
    if url:
        all_product_codes = prepare_unicorn_search(url)
    else:
        # if it breaks but we have all the codes in a file already,
        # or if we just happen to have all the codes in a file already,
        # we no longer need a function parameter. can run this way instead:
        with open('product_codes/product_codes-{}.txt'.format(datetime.date.today()), 'r') as f:
            all_product_codes = [line.strip() for line in f.readlines()]
    print 'narrowed it down to {0} in-store products ....'.format(len(all_product_codes))
    product_urls = make_product_urls(all_product_codes)
    unicorns = unicorn_scrape(product_urls)
    [write_unicorn_json_to_file(unicorn) for unicorn in unicorns]


if __name__ == '__main__':
    url = {'url': 'https://www.lcbapps.lcb.state.pa.us/webapp/Product_Management/psi_ProductListPage_Inter.asp?searchPhrase=&selTyp=&selTypS=&selTypW=&selTypA=&CostRange=&searchCode=&submit=Search'}
    hunt_unicorns(**url)
