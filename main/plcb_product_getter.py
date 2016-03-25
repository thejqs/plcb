#!usr/bin/env python

'''
A crawler to search every product in the
Pennsylvania Liquor Control Board's database, searching for unicorns:
products available for sale in only one retail store in the entire state.
The database is updated at the close of business every day.
Thus every day is a chance for fresh data.
On any given day, given the structure of the PLCB's
product search interfaces, we have about 2,400 pages to crawl
to wade through about 60,000 products to see which are in stores, and then
we can test for unicorns among products that meet initial criteria.

Fun, right?
'''

import requests
import lxml.html
from lxml.cssselect import CSSSelector
import json
# from multiprocessing import Pool


def open_url(url):
    '''
    collects our response object
    '''
    headers = {'user-agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 // Jacob Quinn Sanders, War Streets Media: jacob@warstreetsmedia.com"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.text  # r.content if we need binary
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
    # import ipdb; ipdb.set_trace()
    codes_elements = CSSSelector('td a b font')(tree)
    return [code.text for code in codes_elements if code.text.isdigit()]


def make_search_urls(pages):
    '''
    a generator to help us iterate through the main search pages one at a time.
    the number series the URL structure supports begins with the numeral 2
    '''
    # We've already captured data from one -- our initial -- URL by this point
    for page in xrange(2, pages + 1):
        search_url = 'https://www.lcbapps.lcb.state.pa.us/webapp/Product_Management/psi_ProductListPage_Inter.asp?strPageNum={0}&selTyp=&selTypS=&selTypW=&selTypA=&searchCode=&searchPhrase=&CostRange=&selSale=&strFilter=&prevSortby=BrndNme&sortBy=BrndNme&sortDir=ASC'.format(page)
        yield search_url


def make_product_urls(all_product_codes):
    '''
    a generator to hand off each product-page URL as it gets built
    '''
    for code in all_product_codes:
        product_url = 'http://www.lcbapps.lcb.state.pa.us/webapp/product_management/psi_ProductInventory_Inter.asp?cdeNo={0}'.format(code)
        yield product_url


def parse_search_page(pages):
    '''
    pulls product codes matching our needs from each search page
    '''
    codes = []
    for i, search_url in enumerate(make_search_urls(pages)):
        search_tree = treeify(search_url)
        new_codes = get_product_codes(search_tree)
        codes += new_codes
        print 'collected {0} total codes from {1} pages'.format(len(codes), i + 2)

    return codes


def check_for_unicorn(tree):
    '''
    gives us a quick thumbs-up or thumbs-down on whether each product page
    contains a unicorn
    '''
    check_unicorn = CSSSelector('html body table tr td table tr td font')(tree)
    is_unicorn = False
    if 'one' in check_unicorn[0].text:
        is_unicorn = True
    return is_unicorn


def assemble_unicorn(tree):
    '''
    if a product passes the unicorn test, this gets called to assemble
    our main unicorn object.
    Returns:
    a dict of our object -- a unicorn dict, if you will
    '''
    unicorn_store_elements = CSSSelector('tr td.table-data')(tree)
    unicorn_store = [i.text.strip() for i in unicorn_store_elements]
    unicorn_store_id = unicorn_store[0]
    num_unicorn_bottles = unicorn_store[2]

    unicorn_product_info_elements = CSSSelector('ul li.newsFont b')(tree)
    unicorn_product = [i.text.strip() for i in unicorn_product_info_elements]
    unicorn_code = unicorn_product[0]
    unicorn_name = unicorn_product[1]
    unicorn_bottle_size = unicorn_product[2]
    unicorn_price = unicorn_product[3]

    return {'store_id': unicorn_store_id,
            'name': unicorn_name,
            'price': unicorn_price,
            'bottles': num_unicorn_bottles,
            'product_code': unicorn_code,
            'bottle_size': unicorn_bottle_size}


def on_sale(tree):
    '''
    a separate element, when present. this data gets updated daily,
    so could change. and if we're collecting price, it would be incomplete
    of us not to check this
    '''
    sale_element = CSSSelector('ul li.newsFont b font')(tree)
    if len(sale_element) > 0:
        return [sale.text for sale in sale_element]
    else:
        return 'Not on sale'


def unicorn_scrape(product_urls):
    '''
    collects product data if the product passes the unicorn test
    Returns:
    a list of dicts, each of which contains a unicorn
    '''
    unicorns = []
    for product_url in product_urls:
        product_tree = treeify(product_url)
        is_unicorn = check_for_unicorn(product_tree)
        if not is_unicorn:
            return 'Not a unicorn'
        else:
            unicorn = assemble_unicorn(product_tree)
            unicorn['on_sale'] = on_sale(product_tree)
            unicorns += (unicorn)
            print 'FOUND A UNICORN:', unicorn

    return unicorns


def prepare_unicorn_search(url):
    '''
    assembles everything we need to perform the search,
    getting the heavy lifting of walking all the search pages
    out of the way so we can focus on what we care about.
    Returns:
    a list of product ids we need to append to a url stub
    '''
    tree = treeify(url)
    pages, products = get_total_numbers(tree)
    print 'searching {0} pages and {1} products for unicorns ....'.format(pages, products)
    page_product_codes = get_product_codes(tree)
    print 'found {} initial product codes'.format(len(page_product_codes))
    more_codes = parse_search_page(pages)
    page_product_codes += more_codes

    return page_product_codes


def hunt_unicorns(url):
    '''
    once our product ids are in hand, we can search each product page
    in earnest to ask it whether it is that rarest of beasts
    Note:
    when the search-page servers go down, the product pages stay up.
    so for now, traversing the search pages first to collect the ids we need
    in case anything happens to those servers while we're searching products
    '''
    all_product_codes = prepare_unicorn_search(url)
    print 'narrowed it down to {} in-store products ....'.format(len(all_product_codes))
    product_urls = make_product_urls(all_product_codes)
    unicorns = unicorn_scrape(product_urls)

    print 'here you go: {} unicorns'.format(len(unicorns))
    return unicorns


def write_json_to_file(data):
    '''
    stores our objects in a pprint format
    '''
    print 'writing json ....'
    j = json.dumps(data, indent=4)
    with open('unicorns.json', 'w') as f:
        print >> f, j


def start_scrape():
    '''
    runs the main functions to do the damn thang
    '''
    url = 'https://www.lcbapps.lcb.state.pa.us/webapp/Product_Management/psi_ProductListPage_Inter.asp?searchPhrase=&selTyp=&selTypS=&selTypW=&selTypA=&CostRange=&searchCode=&submit=Search'
    data = hunt_unicorns(url)
    write_json_to_file(data)


start_scrape()
