#!usr/bin/env python

'''
A parser for the daily PDF of the Pennsylvania Liquor Control Board's
retail database.

From this we extract all the ids of products available for sale in one of 597
stores on a given day -- 14,000, give or take -- so we can hand them off to
the main scraper which must check each to discover its boolean boozicorn
status: Is it available in only one store in the state that day?
'''

import pdfquery
import requests
import datetime
import time
import os
import subprocess

from backup_scrapers import multi_plcb_product_getter as mp


def copy_pdf():
    '''
    for now, it's worth keeping a copy of the daily PDF to easily
    check ourselves and make sure we're getting all the data we mean to.
    later, this step can go away and we can operate on the document tree
    given us by the original file
    '''
    # making sure we don't already have a file for today
    if not os.path.isfile('../data/pdfs/plcb_pdf-{0}.pdf'.format(datetime.date.today())):
        # getting just the headers to make sure we want to continue
        pdf_url = 'https://www.lcbapps.lcb.state.pa.us/webapp/Product_Management/Files/productCatalog.PDF'
        req = requests.head(pdf_url)
        d = datetime.date.today()
        # checking the headers to make sure it's from the right date
        if d.strftime('%d %b %Y') in req.headers['last-modified']:  # also check type? req.headers['content-type'] == 'application/pdf'
            r = requests.get(pdf_url)
            with open('../data/pdfs/plcb_pdf-{0}.pdf'.format(datetime.date.today()), 'wb') as f:
                f.write(r.content)
        else:
            print datetime.datetime.now(), "it's the same file as yesterday, hoss, or it ain't there. gimme a few minutes."
            # will try again for a couple hours-plus, every 10 minutes, to see
            # whether the file is updated for the current day
            tries = 0
            while tries < 20:
                time.sleep(600)
                copy_pdf()
                tries += 1
            return None
    else:
        return None


def write_codes_to_file(data):
    '''
    stores our product codes as we go in case of script breakage.
    starting over from scratch sucks and is awful. yes, both of those things

    Args:
    expects an iterable of product codes
    '''
    with open('../data/product_codes/product_codes-{}.txt'.format(datetime.date.today()), 'a+') as f:
        # don't want the result to be a list, just lines of text
        for datum in data:
            print >> f, datum


def get_pdf_codes():
    '''
    calculates the likely position of the first product code and the column
    containing all the codes given a starting point determined from the page
    layout and attempts to slurp up the yummy data thingies.
    '''
    pdf = pdfquery.PDFQuery('../data/pdfs/plcb_pdf-{0}.pdf'.format(datetime.date.today()))
    # should be 600-plus
    pages = pdf.doc.catalog['Pages'].resolve()['Count']
    d = datetime.date.today()
    print 'loading pdf ....'
    # this, um, this takes a while. about 10 minutes. thanks, pdfminer
    pdf.load()
    print 'getting codes ....'
    codes = []
    # there is no page zero
    for page in xrange(1, pages + 1):
        if page > 1:
            # there is no true header row here to help guide us, not in the
            # structure of the page, but we can calculate this based on the
            # first element containing our data.
            try:
                first_code_element = pdf.pq('LTPage[pageid=\'{0}\'] LTTextBoxHorizontal:overlaps_bbox("{1},{2},{3},{4}")'.format(page, 61.45, 551.767, 71, 563.527))[0]
                y_minus = 550
            except IndexError as e:
                print '{} at page {}'.format(e, page)
                print first_code_element
        elif page == 1:
            first_code_element = pdf.pq('LTPage[pageid=\'1\'] LTTextBoxHorizontal:overlaps_bbox("{0},{1},{2},{3}")'.format(61.45, 445.267, 71, 457.027))[0]
            y_minus = 440

        first_code = first_code_element.text.strip()

        x = float(first_code_element.get('x0'))
        y = float(first_code_element.get('y0'))
        # much narrower than this and we miss about 500 of 14,000 product codes
        x_plus = 30

        cells = pdf.extract([('with_formatter', 'text'), ('with_parent', 'LTPage[pageid=\'{0}\']'.format(page)), ('cells', 'LTTextBoxHorizontal:overlaps_bbox("{0},{1},{2},{3}")'.format(x, y - y_minus, x + x_plus, y))])
        new_codes = [c.strip() for c in cells['cells'].split(' ') if c.isdigit() and len(c) >= 3]
        # handles cases where overlaps_bbox grabs, y'know, 'APRICOT' or ''
        if first_code.isdigit():
            new_codes.append(first_code)
        # cleans up a handful of recent years that come in with the codes.
        # seems no matter the x-axis positions, we'll always get a few when
        # they're at the tops of pages and the names of wines are short.
        # something to explore later
        [new_codes.remove(code) for code in new_codes if code[:2] == '20' and int(code) <= int(d.strftime('%Y'))]
        codes += set(new_codes)
        write_codes_to_file(set(new_codes))

    return codes


def collect():
    print 'copying the pdf ....'
    # if the PDF isn't there for us within a few hours of checking,
    # the function will return None and we launch a different scraper
    pdf = copy_pdf()
    if not pdf:
        url = {'url': 'https://www.lcbapps.lcb.state.pa.us/webapp/Product_Management/psi_ProductListPage_Inter.asp?searchPhrase=&selTyp=&selTypS=&selTypW=&selTypA=&CostRange=&searchCode=&submit=Search'}
        codes = mp.prepare_unicorn_search(**url)
    else:
        codes = get_pdf_codes()
    return codes
    print 'done with the pdf'


if __name__ == '__main__':
    collect()
