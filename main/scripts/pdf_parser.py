#!usr/bin/env python

import pdfquery
from pdfquery.cache import FileCache
import requests
import datetime
import time
import os


def copy_pdf():
    '''
    for now, it's worth keeping a copy of the daily PDF to easily
    check ourselves and make sure we're getting all the data we mean to.
    later, this step can go away and we can operate on the document tree
    given us by the original file
    '''
    # making sure we don't have a file for today
    if not os.path.isfile('../static/pdfs/plcb_pdf-{0}.pdf'.format(datetime.date.today()):
        # getting just the headers to make sure we want to continue
        pdf_url = 'https://www.lcbapps.lcb.state.pa.us/webapp/Product_Management/Files/productCatalog.PDF'
        req = requests.head(pdf_url)
        d = datetime.date.today()
        # checking the headers to make sure it's from the right date
        if d.strftime('%d %b %Y') in req.headers['last-modified']:  # also check type? req.headers['content-type'] == 'application/pdf'
            r = requests.get(pdf_url)
            with open('../static/pdfs/plcb_pdf-{0}.pdf'.format(datetime.date.today()), 'wb') as f:
                f.write(r.content)
        else:
            print "it's the same file as yesterday, hoss, or it ain't there. gimme a few minutes."
            time.sleep(600)
            copy_pdf(url)
    else:
        return


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


def get_pdf_codes():
    '''
    calculates the likely position of the first product code and the column
    containing all the codes given a starting point determined from the page
    layout and attempts to slurp up the yummy data thingies.
    '''
    pdf = pdfquery.PDFQuery('../static/pdfs/plcb_pdf-{0}.pdf'.format(datetime.date.today()))
    # should be 600-plus
    pages = pdf.doc.catalog['Pages'].resolve()['Count']
    d = datetime.date.today()
    print 'loading pdf ....'
    # this, um, this takes a while. about 10 minutes
    pdf.load()
    print 'getting codes ....'
    codes = []
    # there is no page zero
    for page in xrange(1, pages + 1):
        if page > 1:
            first_code_element = pdf.pq('LTPage[pageid=\'{0}\'] LTTextBoxHorizontal:overlaps_bbox("{1},{2},{3},{4}")'.format(page, 61.45, 551.767, 68, 563.527))[0]
            y_minus = 550
        elif page == 1:
            first_code_element = pdf.pq('LTPage[pageid=\'1\'] LTTextBoxHorizontal:overlaps_bbox("{0},{1},{2},{3}")'.format(61.45, 445.267, 68, 457.027))[0]
            y_minus = 440

        first_code = first_code_element.text.strip()

        x = float(first_code_element.get('x0'))
        y = float(first_code_element.get('y0'))
        x_plus = 15

        cells = pdf.extract([('with_formatter', 'text'), ('with_parent', 'LTPage[pageid=\'{0}\']'.format(page)), ('cells', 'LTTextBoxHorizontal:overlaps_bbox("{0},{1},{2},{3}")'.format(x, y - y_minus, x + x_plus, y))])
        new_codes = [c.strip() for c in cells['cells'].split(' ') if c.isdigit() and len(c) >= 3]
        if first_code.isdigit():
            new_codes.append(first_code)
        # cleaning up a handful of recent years that come in with the codes.
        # seems no matter the x-axis positions, we'll always get a few when
        # they're at the tops of pages and the names of wines are short.
        # something to explore later
        [new_codes.remove(code) for code in new_codes if code[:2] == '20' and int(code) <= int(d.strftime('%Y'))]
        codes += set(new_codes)
        write_codes_to_file(set(new_codes))

    return codes


def collect():
    print 'copying the pdf ....'
    copy_pdf(pdf_url)
    codes = get_pdf_codes()
    print 'done with the pdf'
    return codes


if __name__ == '__main__':
    collect()
