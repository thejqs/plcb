#!usr/bin/env python

import pdfquery
from pdfquery.cache import FileCache
import requests
import datetime
import time

pdf_url = 'https://www.lcbapps.lcb.state.pa.us/webapp/Product_Management/Files/productCatalog.PDF'


def copy_pdf(pdf_url):
    '''
    for now, it's worth keeping a copy of the daily PDF to easily
    check ourselves and make sure we're getting all the data we mean to.
    later, this step can go away and we can operate on the document tree
    given us by the original file
    '''
    # first getting just the headers to make sure we want to continue
    req = requests.head(pdf_url)
    d = datetime.date.today()
    # checking the headers to make sure it's from the right date
    if d.strftime('%d %b %Y') in req.headers['last-modified']:  # also check type? req.headers['content-type'] == 'application/pdf'
        r = requests.get(pdf_url)
        with open('../static/pdfs/plcb_pdf-{0}.pdf'.format(datetime.date.today()), 'wb') as f:
            f.write(r.content)
    else:
        print "it's the same file as yesterday, hoss. gimme a couple minutes."
        time.sleep(600)
        copy_pdf(url)


# def load_pdf():
#     '''
#     performs the most expensive operation involving the PDF, parsing it into
#     a searchable file object for data extraction
#     '''
#     pdf = pdfquery.PDFQuery('../static/pdfs/new-plcb_pdf-{0}.pdf'.format(datetime.date.today()))
#     # this, um, this takes a while
#     return pdf


# def count_pdf_pages(pdf):
#     '''
#     if we need a page range to traverse, this supplies it
#
#     Args:
#     a loaded PDF file object
#     '''
#     return


# def get_first_element_first_page(pdf):
#     '''
#     collects for us a starting element on which we can do the necessary
#     coordinate calculations to find the rest of our elements
#     '''
#     # first element on first page seems to always be in the same place but
#     # does not always have the same value
#     first_code_element = pdf.pq('LTPage[pageid=\'1\'] LTTextBoxHorizontal:in_bbox("{0},{1},{2},{3}")'.format(61.45, 445.267, 88.3, 457.027))[0]
#     return first_code_element.text.strip()


# def get_first_element_other_pages(pdf):
#     # first element on pages other than the first seem to always be in the same
#     # place but does not always have the same value
#     first_code_element = pdf.pq('LTPage[pageid=\'2\'] LTTextBoxHorizontal:in_bbox("{0},{1},{2},{3}")'.format(65.95, 551.767, 88.325, 563.527))[0]
#     return first_code_element


def write_codes_to_file(data):
    '''
    stores our product codes as we go in case of script breakage.
    starting over from scratch sucks and is awful. yes, both of those things

    Args:
    expects an iterable of product codes
    '''
    with open('../static/pdfs/product_codes-{}.txt'.format(datetime.date.today()), 'a+') as f:
        # don't want the result to be a list, just lines of text
        for datum in data:
            print >> f, datum


# def find_codes(pdf, elem, page):
#     '''
#     given a place to look on the page for a starting element and the
#     page number in the document,
#     '''
#     x = float(elem.get('x0'))
#     y = float(elem.get('y0'))
#     x_plus = 35
#     if page > 1:
#         y_minus = 520
#     elif page == 1:
#         y_minus = 400
#     # returns a dict with 'cells' as the key and a value of one string
#     # containing our space-separated codes
#     cells = pdf.extract([('with_formatter', 'text'), ('with_parent', 'LTPage[pageid=\'{0}\']'.format(page)), ('cells', 'LTTextBoxHorizontal:in_bbox("{0},{1},{2},{3}")'.format(x, y - y_minus, x + x_plus, y))])
#     return [c.strip() for c in cells['cells'].split(' ')]


def get_pdf_codes():
    '''
    calculates the likely position of the first product code and the column
    containing all the codes given a starting point determined from the page
    layout and attempts to slurp up the yummy data thingies.
    '''
    pdf = pdfquery.PDFQuery('../static/pdfs/plcb_pdf-{0}.pdf'.format(datetime.date.today()))
    pages = pdf.doc.catalog['Pages'].resolve()['Count']
    start_load = datetime.datetime.now()
    print 'loading pdf ....'
    print start_load
    pdf.load()
    end_load = datetime.datetime.now()
    print end_load
    print end_load - start_load

    print 'getting codes ....'
    start_codes = datetime.datetime.now()
    print start_codes

    codes = []
    first_codes = []
    first_codes_raw = []
    for page in xrange(1, pages + 1):
        if page > 1:
            first_code_element = pdf.pq('LTPage[pageid=\'{}\'] LTTextBoxHorizontal:overlaps_bbox("{},{},{},{}")'.format(page, 61.45, 551.767, 88.3, 563.527))[0]
            y_minus = 550
        elif page == 1:
            first_code_element = pdf.pq('LTPage[pageid=\'1\'] LTTextBoxHorizontal:overlaps_bbox("{0},{1},{2},{3}")'.format(61.45, 445.267, 88.3, 457.027))[0]
            y_minus = 440

        first_codes_raw.append(first_element.text)

        first_code = first_code_element.text.strip()

        first_codes.append(first_code)

        x = float(first_code_element.get('x0'))
        y = float(first_code_element.get('y0'))
        x_plus = 15

        cells = pdf.extract([('with_formatter', 'text'), ('with_parent', 'LTPage[pageid=\'{0}\']'.format(page)), ('cells', 'LTTextBoxHorizontal:overlaps_bbox("{0},{1},{2},{3}")'.format(x, y - y_minus, x + x_plus, y))])
        new_codes = [c.strip() for c in cells['cells'].split(' ') if c and c.isdigit() and len(c) >= 3]
        if first_code.isdigit():
            new_codes.append(first_code)
        codes += set(new_codes)
        write_codes_to_file(set(new_codes))

    end_codes = datetime.datetime.now()
    print end_codes
    print 'found {} codes in {}'.format(len(codes), end_codes - start_codes)
    return codes


def collect():
    print 'copying the pdf ....'
    copy_pdf(pdf_url)
    # print 'starting pdf load ....'
    # pdf = load_pdf()
    codes = get_pdf_codes()
    print 'done with the pdf'
    return codes


if __name__ == '__main__':
    pdf_url = 'https://www.lcbapps.lcb.state.pa.us/webapp/Product_Management/Files/productCatalog.PDF'
