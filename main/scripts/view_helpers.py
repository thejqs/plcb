#!usr/env/bin python

from collections import Counter
import datetime
import json
import re
from operator import itemgetter

from main.models import Store, Unicorn
from project.settings_local import day_switcher


def find_median(lst):
    '''
    given a list, we find or compute the median value
    '''
    l = sorted(lst)
    len_l = len(lst)
    if len_l < 1:
        return 'you are a silly person. nothing in this list'
    idx = (len_l - 1) // 2
    if len_l % 2:
        return l[idx]
    else:
        return (l[idx] + l[idx + 1]) / 2.0

def sort_by_price(lst):
    '''
    a one-liner, but one we'll use repeatedly.
    would otherwise be a lambda

    Args:
    a list of dictionaries, which each contain 'price' keys
    '''
    return sorted(lst, key=lambda k: k.price, reverse=True)

def find_top_stores(lst):
    '''
    given a list, finds the number of occurrences of each item, returning
    the most-common value
    '''
    return Counter(lst).most_common(10)
    # return max([(x, lst.count(x)) for x in lst], key=itemgetter(1))

def top_10_price_minus_sale_price(lst_of_objs):
    '''
    given a list of Django objects, each of which contains 'price' and
    'on_sale_price' attributes, finds the largest gaps between retail
    price and sale price -- in other words, the most deeply discounted
    products in real dollars

    Returns:
    the top 10
    '''
    s = (c for c in lst_of_objs if c.on_sale_price > 0)
    return sorted(s, key=lambda k: k.price - k.on_sale_price, reverse=True)[:10]

def top_10_percent_discount(lst_of_objs):
    '''
    given a list of Django objects, each of which contains 'price' and
    'on_sale_price' attributes, finds the largest percentage gaps between
    retail price and sale price for products retailing for at least $20 --
    in other words, the most deeply discounted products by percentage
    in that range

    Returns:
    the top 10
    '''
    s = (c for c in lst_of_objs if c.on_sale_price > 0 and c.price > 20)
    return sorted(s, key=lambda k: 1 - (k.on_sale_price / k.price), reverse=True)[:10]


def search_boozicorns(form, context_dict):
    # so the search box will allow extra spaces but they won't make it
    # into the queries
    search = form.cleaned_data['name'].strip()
    response = Unicorn.objects.filter(name__icontains=search).filter(scrape_date=day_switcher['today'].strftime('%Y-%m-%d'))  # today.strftime('%Y-%m-%d')
    # no matches returns an empty list;
    # no matches could mean the day's data isn't yet available and
    # that's no reason to break
    if not response:
        response = Unicorn.objects.filter(name__icontains=search).filter(scrape_date=day_switcher['yesterday'].strftime('%Y-%m-%d'))

    # if we have a match, we want the whole object available,
    # not just the matching portion;
    # if statement here because why bother with operations on
    # an empty list
    if response:
        clean_response = [r for r in response for m in [re.search(r'(?<=\b)({0}\b)'.format(search.lower()), r.name.lower())] if m]
        ordered_clean_response = sorted(clean_response, key=lambda k: k.name)
        context_dict['unicorn_response'] = ordered_clean_response
    else:
        context_dict['unicorn_response'] = response

    return context_dict['unicorn_response']


if __name__ == '__main__':
    find_median()
