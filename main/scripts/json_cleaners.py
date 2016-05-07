#!usr/bin/env python

'''
a small collection of functions used to clean and standardize the earliest
files of our scraper data, which, y'know, needed it.
'''

import json
import re


# needed for unicorns-2016-03-26.json
def clean_first_json_file(path):
    '''
    The first full successful scrape of this data needed a few format changes
    that no other file needed in order to standardize it
    '''
    json_file = json.load(open(path, 'r'))
    with open('../new_unicorns-2016-03-26.json', 'a+') as outfile:
        new_u = []
        for unicorn in json_file:
            unicorn['price'] = float(unicorn['price'].replace('$', '').replace(',', ''))
            unicorn['on_sale'] = float(unicorn['on_sale'][0].replace('Sale Price: $', '').replace(',', '')) if 'Sale' in unicorn['on_sale'][0] else False
            num_unicorn_bottles_pattern = '(^\d+(?!\S))'
            unicorn['bottles'] = int(re.match(num_unicorn_bottles_pattern, unicorn['bottles']).group())
            new_u.append(unicorn)

        j = json.dumps(new_u, sort_keys=True, indent=4)
        print >> outfile, j


# needed for a few files that were not properly Python-formatted as a list of dicts
def format_early_json(path):
    '''
    a handful of files were formatted improperly as one dict after another
    as opposed to a true list of dicts
    '''
    file_date_pattern = '((?<=\-)\d+.*(?=\.))'
    file_date = re.search(file_date_pattern, path).group()
    with open(path, 'r') as f:
        with open('new_data/unicorns-' + file_date, 'a+') as outfile:
            for line in f:
                json_line = line.replace('}', '},')
                print >> outfile, json_line


# for those files created before scrape_date was included as a JSON field
def add_scrape_date(path):
    '''
    gives us to add the scrape_date field, borrowed from
    a substring of the filename
    '''
    file_date_pattern = '((?<=\-)\d+.*(?=\.))'
    file_date = re.search(file_date_pattern, path).group()
    f = json.load(open(path, 'r'))
    with open('new_data/unicorns-{}.json'.format(file_date), 'a+') as outfile:
        for unicorn in f:
            unicorn['scrape_date'] = file_date

        j = json.dumps(f, sort_keys=True, indent=4)
        print >> outfile, j


if __name__ == '__main__':
    add_scrape_date()
