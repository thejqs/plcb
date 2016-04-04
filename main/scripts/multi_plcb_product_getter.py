#!usr/bin/env python

'''
A crawler to search every product in the
Pennsylvania Liquor Control Board's database, searching for unicorns:
products available for sale in only one retail store in the entire state.

Configured to use Python's multiprocessing module --
thus I can't use generators everywhere I'd like.
Life is just hard sometimes. Boo. Also hoo.

The PLCB claims the database is updated at the close of business every day,
but it's more like 5 a.m. the following day. Nonetheless, that's still before
stores open for the day. Every day is a chance for fresh data.

The site is pretty brittle. It doesn't take that many concurrent requests
for it to get unreliable. So we have to be more than a little careful
how we hit it.

On any given day, given the structure of the PLCB's
product search interfaces, we have about 2,400 pages to crawl
to wade through about 60,000 products to see the 14,000 or so
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
import time
from multiprocessing import Pool


def open_url(url):
    '''
    collects our response object
    '''
    try:
        # read_timeout = 5.0 // tried this but the servers are too damn slow to respond
        headers = {'user-agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 // Jacob Quinn Sanders, War Streets Media: jacob@warstreetsmedia.com"}
        r = requests.get(url, headers=headers)  # timeout=(10.0, read_timeout)
        if r.status_code == 200:
            return r.text
        else:
            print 'You got a {0} error from {1}'.format(r.status_code, r.url)
            raise Exception('You are an idiot. Bad link.')
    except requests.exceptions.ReadTimeout as e:
        print e
        print 'no delicious bytes to eat getting {0}'.format(url)


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
    j = json.dumps(data, sort_keys=True, indent=4)
    with open('../unicorns_json/unicorns-{}.json'.format(datetime.date.today()), 'a+') as f:
        print >> f, j


def write_codes_to_file(data):
    '''
    a function to store our product codes as we go in case of script breakage

    Args:
    expects an iterable
    '''
    with open('../product_codes/product_codes-{}.txt'.format(datetime.date.today()), 'a+') as f:
        for datum in data:
            # don't want the result to be a list, just lines of text
            print >> f, datum


def get_total_numbers(tree):
    '''
    collects the total number of pages and products we have to crawl.
    they come in as strings with extra words and a comma we have to handle
    '''
    time.sleep(1)
    nums = CSSSelector('form table tr td')(tree)
    num_pages = int(''.join(n for n in nums[0].text[10:].split(',')))
    num_products = int(''.join(n for n in nums[1].text[25:].split(',')))

    return (num_pages, num_products)


def get_product_codes(url):
    '''
    mapped to a list of DOM trees, collects the product codes that will complete
    our product-page URLs so we can check each for unicorns
    '''
    codes_elements = happy_little_search_trees(url)  # CSSSelector('td a b font')(tree)
    # we have to ignore a 'New Search' string that comes in here
    codes = [code.text for code in codes_elements if code.text.isdigit()]
    write_codes_to_file(codes)

    # print 'wrote {0} codes'.format(len(codes))
    return codes


def make_search_urls(pages):
    '''
    creates a list of urls so we can iterate over the main search pages.
    the number series the URL structure supports begins with the numeral 2.
    we have already collected data off the initial search page by this point

    Args:
    the total number of pages to search
    '''
    search_urls = []
    # We've already captured data from one -- our initial -- URL by this point
    for page in xrange(2, pages + 1):
        search_url = 'https://www.lcbapps.lcb.state.pa.us/webapp/Product_Management/psi_ProductListPage_Inter.asp?strPageNum={0}&selTyp=&selTypS=&selTypW=&selTypA=&searchCode=&searchPhrase=&CostRange=&selSale=&strFilter=&prevSortby=BrndNme&sortBy=BrndNme&sortDir=ASC'.format(page)
        search_urls.append(search_url)
    return search_urls


def make_product_urls(codes):
    '''
    Args:
    a list of all product ids
    '''
    product_urls = []
    for code in codes:
        product_url = 'http://www.lcbapps.lcb.state.pa.us/webapp/product_management/psi_ProductInventory_Inter.asp?cdeNo={0}'.format(code)
        product_urls.append(product_url)
    return product_urls


def happy_little_search_trees(url):
    '''
    an unpacker for DOM elements into parseable lists
    of the text from those elements
    '''
    tree = treeify(url)
    return CSSSelector('td a b font')(tree)


def check_for_unicorn(tree):
    '''
    gives us a quick thumbs-up or thumbs-down on whether each product page
    contains a unicorn. expects to operate on the parsed DOM tree
    of a product page
    '''
    check_unicorn = CSSSelector('body table tr td table tr td font')(tree)
    is_unicorn = False
    if 'one Location' in check_unicorn[0].text:
        is_unicorn = True
    return is_unicorn


def assemble_unicorn(tree):
    '''
    if a product passes the unicorn test, this gets called to assemble
    our main unicorn object. expects to operate on the parsed DOM tree
    of a product page

    Returns:
    a dict of most of our object -- a unicorn dict, if you will
    '''
    unicorn_store_elements = CSSSelector('tr td.table-data')(tree)
    unicorn_store = [i.text.strip() for i in unicorn_store_elements]
    # would wrap this next bit in a try-except but it only breaks if the target
    # data is being updated -- which is a good time to break
    unicorn_store_id = unicorn_store[0]
    # there can be as many as three digits at the beginning of each
    # number-of-units string for sure and theoretically more.
    # hence the regex to handle the variations in number of digits.
    # preceded by the .replace() on the off-chance inventory is >1000
    # as strings of four-digit numbers on this site all carry commas
    num_unicorn_bottles = unicorn_store[2].replace(',', '')
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


def on_sale(tree):
    '''
    a separate element, when present. this data gets updated daily,
    this could change, even if the unicorn remains a unicorn.
    and if we're collecting price, it would be incomplete of us
    not to check this

    Returns:
    a list-encased string for whether each unicorn item was on sale
    for addition to each unicorn dict, else False
    '''
    sale_element = CSSSelector('ul li.newsFont b font')(tree)
    if len(sale_element) > 0:
        return sale_element[0].text
    else:
        return False


def unicorn_scrape(trees):
    '''
    collects product data if the product passes the unicorn test.
    operates on a product-page DOM tree

    Returns:
    a list of unicorn dicts, each of which contains a unicorn
    '''
    # print "searching ...."
    unicorns = []
    for tree in trees:
        is_unicorn = check_for_unicorn(tree)
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
            # print i, 'FOUND A UNICORN:', unicorn
    print 'found {0} unicorns ....'.format(len(unicorns))
    return unicorns


def search_first_page(url):
    '''
    collects data from the very first search page, which doesn't really
    fit the URL structure for the rest of the search pages. gotta
    start somewhere.

    Returns:
    the total pages we will have to search and our first product codes
    '''
    tree = treeify(url)
    try:
        pages, products = get_total_numbers(tree)
    except IndexError as e:
        print e
        print 'uh-oh. is the page down? we should check: '
        r = requests.get(url)
        print r.text
        print r.status_code

    print 'searching {0} pages and {1} products for unicorns ....'.format(pages, products)
    page_product_codes = get_product_codes(url)
    print 'found {0} initial product codes'.format(len(page_product_codes))
    return pages, page_product_codes


def prepare_unicorn_search(url):
    '''
    assembles everything we need to perform the search,
    getting the heavy lifting of walking all the search pages
    out of the way so we can focus on what we care about.

    Args:
    an initial URL on which to begin and a pool of multiprocessing workers

    Returns:
    a list of product ids we need to append to a url stub
    '''
    start_search = datetime.datetime.now()
    print start_search

    pages, page_product_codes = search_first_page(url)
    search_urls = make_search_urls(pages)
    print 'num_search_urls: {}'.format(len(search_urls))
    print 'getting codes ....'
    new_codes = (code for code in p.imap_unordered(get_product_codes, search_urls))
    # should redo some of this, as we're unpacking (sometimes) nested lists
    # when we could unpack as we go and only have one list to deal with here.
    # meantime, bless the double list comprehension
    page_product_codes += [c for code in new_codes for c in code if len(c) > 1]

    end_search = datetime.datetime.now()
    print 'found {0} product codes ....'.format(len(page_product_codes))
    print end_search
    print end_search - start_search
    return page_product_codes


def hunt_unicorns(url=None):
    '''
    once our product ids are in hand, we can search each product page
    in earnest to ask it whether it is that rarest of beasts

    Args:
    if using: a url on which to begin running these functions.
    if product codes are already in hand -- stashed in a text file, say --
    can run based on those with no args

    Returns:
    a JSON-serializable list of unicorn dicts

    Note:
    when the search-page servers go down, the product pages stay up.
    so for now, traversing the search pages first and separately
    to collect the ids we need in case anything goes wonky with those servers
    while we're searching products
    '''
    start_products = datetime.datetime.now()
    print start_products

    if url:
        all_product_codes = prepare_unicorn_search(url)
    else:
        # if it breaks but we have all the codes already,
        # we no longer need a parameter. can also run this way instead:
        # for yesterday: datetime.date.today() - datetime.timedelta(days=1)
        with open('../product_codes/product_codes-{}.txt'.format(datetime.date.today()), 'r') as f:
            all_product_codes = [line.strip() for line in f.readlines()]
    print 'narrowed it down to {0} in-store products ....'.format(len(all_product_codes))
    product_urls = make_product_urls(all_product_codes)
    print 'made {0} urls ....'.format(len(product_urls))
    print 'getting product urls ....'
    # multiprocessing can't handle lxml DOM tree elements.
    # so granularly we go
    rs = (u for u in p.imap_unordered(open_url, product_urls))
    print 'making DOM trees ... happy little DOM trees ....'
    trees = (parse_html(r) for r in rs)
    print 'hunting unicorns ....'
    unicorns = unicorn_scrape(trees)
    print 'writing unicorns to json ....'
    [write_unicorn_json_to_file(unicorns) for unicorn in unicorns]
    print 'done hunting.'
    end_products = datetime.datetime.now()
    print end_products - start_products
    print 'all cleaned up. long day. tacos?'


if __name__ == '__main__':
    p = Pool(8)
    url = {'url': 'https://www.lcbapps.lcb.state.pa.us/webapp/Product_Management/psi_ProductListPage_Inter.asp?searchPhrase=&selTyp=&selTypS=&selTypW=&selTypA=&CostRange=&searchCode=&submit=Search'}
    hunt_unicorns(**url)
    # hunt_unicorns()
