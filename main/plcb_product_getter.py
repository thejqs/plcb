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


def make_product_urls(all_product_codes):
    '''
    a generator to hand off each product-page URL as it gets built
    '''
    for code in all_product_codes:
        product_url = 'http://www.lcbapps.lcb.state.pa.us/webapp/product_management/psi_ProductInventory_Inter.asp?cdeNo={0}'.format(code)
        yield product_url


def make_search_urls(tree, pages):
    '''
    a generator to help us iterate through the main search pages one at a time
    '''
    for page in xrange(2, pages - 2):
        search_url = 'https://www.lcbapps.lcb.state.pa.us/webapp/Product_Management/psi_ProductListPage_Inter.asp?strPageNum={0}&selTyp=&selTypS=&selTypW=&selTypA=&searchCode=&searchPhrase=&CostRange=&selSale=&strFilter=&prevSortby=BrndNme&sortBy=BrndNme&sortDir=ASC'.format(page)
        yield search_url


def parse_search_page(search_urls):
    '''
    pulls product codes matching our needs from each search page
    '''
    for url in search_urls:
        tree = treeify(url)
        return get_product_codes(tree)


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
    a dict of our object
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
    collects product data if the product passes
    the unicorn test
    '''
    for url in product_urls:
        tree = treeify(url)
        is_unicorn = check_for_unicorn(tree)
        if not is_unicorn:
            return 'Not a unicorn'
        else:
            unicorn = assemble_unicorn(tree)
            on_sale = on_sale(tree)
            unicorn['on_sale'] = on_sale
            return unicorn


def prepare_unicorn_search(url):
    '''
    assembles everything we need to perform the search,
    getting the heavy lifting of walking all the search pages
    out of the way so we can focus on what we care about.
    Returns:
    a list of product ids we need to append to a url stub
    '''
    all_product_codes = []
    tree = treeify(url)
    pages, products = get_total_numbers(tree)
    print 'searching {0} pages and {1} products for unicorns ....'.format(pages, products)
    page_product_codes = get_product_codes(tree)
    all_product_codes.append(page_product_codes)
    search_urls = make_search_urls(tree, pages)
    more_page_product_codes = parse_search_page(search_urls)
    all_product_codes.append(more_page_product_codes)
    return all_product_codes


def hunt_unicorns(url):
    '''
    once our product ids are in hand, we can search each product page
    in earnest to ask it whether it is that rarest of beasts
    '''
    unicorns = []
    all_product_codes = prepare_unicorn_search(url)
    print 'narrowed it down to {} in-store products ....'.format(len(all_product_codes))
    product_urls = make_product_urls(all_product_codes)
    unicorn = unicorn_scrape(product_urls)
    if unicorn != 'Not a unicorn':
        print 'FOUND A UNICORN:', unicorn
        unicorns.append(unicorn)

    print unicorns
    return unicorns


hunt_unicorns('https://www.lcbapps.lcb.state.pa.us/webapp/Product_Management/psi_ProductListPage_Inter.asp?searchPhrase=&selTyp=&selTypS=&selTypW=&selTypA=&CostRange=&searchCode=&submit=Search')
