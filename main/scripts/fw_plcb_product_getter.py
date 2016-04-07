#!usr/bin/env python

'''
A crawler to search every product in the
Pennsylvania Liquor Control Board's database, searching for unicorns:
products available for sale in only one retail store in the entire state.

Configured to use Python's multiprocessing module -- thus I can't
use generators everywhere I'd like. Life is just hard sometimes. Boo. Also hoo.

The PLCB claims the database is updated at the close of business every day,
but it's more like 5 a.m. the following day. Nonetheless, that's still before
stores open for the day.

Every day is a chance for fresh data.

The target site to collect product ids is the PLCB's main site.
The checking of individual products to see which stores they're in happns on
a secondary site. The main reason there is that the search interface on
the secondary site is brittle and not easy to reconfigure. It has to serve
too many pages for us to get all thr product ids. So we have to be more
than a little careful how we hit it.

On any given day, given the structure of the PLCB's
product-search interface on the secondary site, we would have about 2,400 pages
to crawl in order to wade through about 60,000 products to see the 14,000 or so
in stores. This way we hit about dozen pages -- but some of the
product codes are missing. Still investigating.

Once we have product codes, we can test for unicorns, which usually number
about 2,000.

Fun, right?
'''

import requests
import StringIO
from lxml import etree
import lxml.html
from lxml.cssselect import CSSSelector
import json
import datetime
import re
import time
from multiprocessing import Pool


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
        print e
        print 'no delicious bytes to eat getting {0}'.format(url)


def parse_html(unparsed_html):
    '''
    an initial parse of raw html

    Returns:
    a DOM tree
    '''
    parser = etree.HTMLParser()
    return etree.parse(StringIO.StringIO(unparsed_html), parser)


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
    with open('new_unicorns-{}.json'.format(datetime.date.today()), 'a+') as f:
        print >> f, j


def write_codes_to_file(data):
    '''
    stores our product codes as we go in case of script breakage.
    starting over from scratch sucks and is awful. yes, both of those things

    Args:
    expects an iterable of product codes
    '''
    with open('product_codes-{}.txt'.format(datetime.date.today()), 'a+') as f:
        # don't want the result to be a list, just lines of text
        for datum in data:
            print >> f, datum


def assemble_categories():
    '''
    these are not in a simple place to grab on the page and they are
    just inconsistent enough to assemble from other values. so here
    we stash them in a dict for easy retrieval later when we need to add
    them to url stubs
    '''
    booze_categories = {}
    booze_categories['Wines+by+Variety'] = ['WbV_Red',
                                            'WbV_White']
    booze_categories['Spirits'] = ['S_Other',
                                   'S_Cocktails+and+Mixers',
                                   'S_Irish+Whiskey',
                                   'S_Canadian+Whiskey',
                                   'S_Bourbon',
                                   'S_American+Whiskey',
                                   'S_Vodka',
                                   'S_Tequila',
                                   'S_Rum',
                                   'S_Single+Malts',
                                   'S_Blended+Scotch+Whiskey',
                                   'S_Gin',
                                   'S_Cordials',
                                   'S_Cognac',
                                   'S_Brandy']
    booze_categories['Other'] = ['O_Vermouth',
                                'O_Sake',
                                'O_RoseBlush',
                                'O_Organic',
                                'O_Kosher',
                                'O_Beverage',
                                'O_Dessert',
                                'O_Cider']
    booze_categories['Sparkling'] = ['']
    # the Chairman's Selection category contains codes
    # that already exist in their native categories
    return booze_categories


def make_search_urls(booze_categories):
    '''
    expects a dictionary from which we can withdraw the values we need to complete the urls. wine categories
    and those for spirits have slightly different url structures
    '''
    for key in booze_categories.keys():
        for value in booze_categories[key]:
            if key == 'Spirits':
                search_url = 'http://www.finewineandgoodspirits.com/webapp/wcs/stores/servlet/SpiritsCatalogSearchResultView?tabSel=2&sortBy=&sortDir=&storeId=10051&catalogId=258552&langId=-1&parent_category_rn={0}&newsearchlist=no&resetValue=2&searchType={0}&minSize=&maxSize=&promotions=&rating=&vintage=&specificType=&price=&maxPrice=0&varitalCatIf=&region=&country=&varietal=&listSize=10000&searchKey=&pageNum=1&totPages=1&level0={0}&level1={1}&level2=&level3=&keyWordNew=false&VId=&TId=&CId=&RId=&PRc=&FPId=&TRId=&ProId=&isKeySearch=&SearchKeyWord=Name+or+Code'.format(key, value)

            else:
                search_url = 'http://www.finewineandgoodspirits.com/webapp/wcs/stores/servlet/CatalogSearchResultView?tabSel=2&sortBy=&sortDir=&storeId=10051&catalogId=258552&langId=-1&parent_category_rn=Wines+by+Variety&newsearchlist=no&resetValue=2&searchType=WINE&minSize=&maxSize=&promotions=&rating=&vintage=&specificType=&price=0&maxPrice=0&varitalCatIf=&region=&country=&varietal=&listSize=10000&searchKey=&pageNum=1&totPages=1&level0={0}&level1={1}&level2=&level3=&keyWordNew=false&VId=&TId=&CId=&RId=&PRc=&FPId=&TRId=&ProId=&isKeySearch=&SearchKeyWord=Name+or+Code'.format(key, value)

            yield search_url


def get_total_numbers(tree):
    '''
    collects from each section page the total number of products
    we have to crawl.

    Args:
    a DOM tree
    '''
    time.sleep(1)
    try:
        num_products_string = tree.xpath('//div[@class="tabSelected"]/text()')[0]
    except IndexError:
        num_products_string = tree.xpath('//div[@class="tabSelected_blue"]/text()')[0]
    # regex to be sure the digits are contained in parentheses and thus match
    # the known string pattern -- or else we don't want them
    print num_products_string
    num_pattern = '((?<=\()\d+(?=\)))'
    num_products = re.search(num_pattern, num_products_string).group()
    return num_products


def get_product_codes(tree, wine=None):
    '''
    collects the product codes that will complete
    our product-page URLs so we can check each for unicorns

    Args:
    a DOM tree and a boolean for whether the page contains
    wine products or not, which need to be extracted
    a little differently.

    Returns:
    a list of product codes
    '''
    labels = tree.xpath('//div[@class="textTop"]/div/span/text()')
    # for some reason the text values we want here require the granularity
    # of xpath. css selectors miss them
    if wine:
        codes_only = wine_codes(tree, labels)
    else:
        codes_only = booze_codes(tree)
    # killing leading zeroes -- there are sometimes none, sometimes four,
    # sometimes five, and possibly more -- to append them to a url stub
    code_anti_pattern = '^([0]+)'
    return [re.sub(code_anti_pattern, '', code) for code in codes_only]


def wine_codes(tree, labels):
    '''
    to extract ids for wine products, we have to parse
    product vintage, unit size and the code itself.
    '''
    vintage_size_code = tree.xpath('//div[@class="textTop"]/div/text()')
    zipped = zip(labels, vintage_size_code)
    # making sure they're strings and not unicode
    return [str(c[1].strip()) for c in zipped if 'Code' in c[0]]


def booze_codes(tree):
    '''
    non-wine products don't have a vintage, thus need to
    be handled a little differently.
    '''
    return [str(e.strip()) for e in tree.xpath('//div[@class="textTop"]/div/text()') if not ' ' in e]


def make_product_urls(codes):
    '''
    creates the urls we need to check for unicorns

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
        print 'no text to check here? that would be weird.'
        print [c.text for c in check_unicorn]


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
        print e
        print unicorn_store
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


def collect_codes():
    '''
    combs each search url for product ids to hand off
    to a unicorn-hunter
    '''
    start_search = datetime.datetime.now()
    print start_search

    codes = []
    booze_categories = assemble_categories()
    search_urls = (u for u in make_search_urls(booze_categories))
    for url in search_urls:
        tree = treeify(url)
        nums = get_total_numbers(tree)
        if 'WINE' in url:
            new_codes = get_product_codes(tree, wine=True)
        else:
            new_codes = get_product_codes(tree, wine=False)
        write_codes_to_file(new_codes)
        codes += new_codes
        print 'up to {} codes ....'.format(len(codes))

    end_search = datetime.datetime.now()
    print len(codes)
    print len(set(codes))
    print 'found {0} product codes ....'.format(len(codes))
    print end_search
    print end_search - start_search
    with open('new_product_codes_set.txt', 'a+') as f:
        for code in set(codes):
            print >> f, code
    return set(codes)


def hunt_unicorns():
    '''
    once our product ids are in hand, we can search each product page
    in earnest to ask it whether it is that rarest of beasts
    '''
    codes = collect_codes()
    start_products = datetime.datetime.now()
    print start_products
    product_urls = make_product_urls(codes)
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

    end_products = datetime.datetime.now()
    print end_products - start_products
    print 'all cleaned up. long day. tacos?'


if __name__ == '__main__':
    p = Pool(8)
    hunt_unicorns()
