import os, sys
from django.shortcuts import render
from django.views.generic import View
from django.conf import settings
from collections import Counter
import datetime
import json
from operator import itemgetter


# Create your views here.
# def ascii_encode_dict(data):
#     ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x
#     return dict(map(ascii_encode, pair) for pair in data.items())


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
    return sorted(lst, key=itemgetter('price'), reverse=True)


def unicorns(request):
    context = {}
    unicorns_dict = {}
    today = datetime.date.today()
    # if today's data file doesn't exist, we'll use yesterday's.
    # will help for those cases after midnight and before we have fresh data
    try:
        f = open(os.path.join(settings.BASE_DIR, 'main/data/unicorns_json/unicorns-{}.json'.format(today)), 'r')
        unicorns_dict['scrape_date'] = today.strftime('%Y-%m-%d')
    except IOError:
        f = open(os.path.join(settings.BASE_DIR, 'main/data/unicorns_json/unicorns-{}.json'.format(today - datetime.timedelta(days=1))), 'r')
        unicorns_dict['scrape_date'] = (today - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    unicorns_json = json.load(f)  # , object_hook=ascii_encode_dict
    # don't need an open file no mo'
    f.close()
    max_price = None
    min_price = None
    min_name = None
    max_name = None
    most_bottles = None
    most_bottles_price = None
    most_bottles_on_sale = None
    most_bottles_name = None
    most_bottles_store_id = None
    stores = []
    whiskey = []
    rum = []
    agave = []
    gin = []
    fancy = []

    all_prices = [u['price'] for u in unicorns_json]
    most_common_price = Counter(all_prices).most_common()[0]
    median_price = find_median(all_prices)

    # capturing our various summary data in one loop through the JSON objects
    for unicorn in unicorns_json:
        name = unicorn['name']
        num_bottles = int(unicorn['bottles'])
        price = float(unicorn['price'])
        on_sale = unicorn['on_sale']
        stores.append(unicorn['store_id'])

        if price > 100:
            fancy.append(unicorn)

        if 'Whiskey' in name and unicorn not in whiskey:
            whiskey.append(unicorn)
        if 'Bourbon' in name and unicorn not in whiskey:
            whiskey.append(unicorn)
        if 'Scotch' in name and unicorn not in whiskey:
            whiskey.append(unicorn)
        if 'Rum' in name and unicorn not in rum:
            rum.append(unicorn)
        if 'Tequila' in name and unicorn not in agave:
            agave.append(unicorn)
        if 'Mezcal' in name and unicorn not in agave:
            agave.append(unicorn)
        if 'Gin' in name and 'Ginjo' not in name and unicorn not in gin:
            gin.append(unicorn)

        if (min_price is None or min_price > price) and price > 1 and unicorn['bottle_size'] != 'EACH':
            min_price = price
            min_name = name
        if max_price is None or max_price < price:
            max_price = price
            max_name = name
        if most_bottles is None or most_bottles < num_bottles:
            most_bottles = num_bottles
            most_bottles_name = name
            most_bottles_price = price
            most_bottles_on_sale = 'Sale price: ${}'.format(unicorn['on_sale']) if unicorn['on_sale'] else None
            most_bottles_store_id = unicorn['store_id']

    count_stores = [(x, stores.count(x)) for x in stores]
    top_store = max(count_stores, key=itemgetter(1))

    if today.strftime('%Y-%m-%d') in f.name:
        unicorns_dict['data_date'] = '{}'.format(today.strftime('%d %B %Y'))
    elif (today - datetime.timedelta(days=1)).strftime('%Y-%m-%d') in f.name:
        unicorns_dict['data_date'] = '{}'.format((today - datetime.timedelta(days=1)).strftime('%d %B %Y'))
    unicorns_dict['mode'] = most_common_price
    unicorns_dict['median'] = median_price
    unicorns_dict['min'] = [min_name.lower(), '${}'.format(min_price)]
    unicorns_dict['max'] = [max_name.lower(), '${}'.format(max_price)]
    unicorns_dict['bottles'] = [most_bottles_name.lower(), most_bottles, '${}'.format(most_bottles_price), most_bottles_on_sale]
    unicorns_dict['whiskey'] = [len(whiskey), sort_by_price(whiskey)]
    unicorns_dict['rum'] = [len(rum), sort_by_price(rum)]
    unicorns_dict['agave'] = [len(agave), sort_by_price(agave)]
    unicorns_dict['gin'] = [len(gin), sort_by_price(gin)]
    unicorns_dict['fancy'] = [len(fancy), sort_by_price(fancy)]

    top_store_contents = [unicorn for unicorn in unicorns_json if unicorn['store_id'] == top_store[0]]

    with open('main/data/stores/retail_stores-2016-04-10.json', 'r') as f:
        stores_json = json.load(f)  # , object_hook=ascii_encode_dict
        # don't want to have to manually update the number of stores
        # in the intro text should it change with a new scrape for store data
        unicorns_dict['num_stores'] = len(stores_json)
        store_data = None
        for store in stores_json:
            if top_store[0] == store['id']:
                address = store['address']
                phone = store['phone']
                store_type = store['store_type']
            if most_bottles_store_id == store['id']:
                unicorns_dict['bottles'].append(store['address'].lower())
        unicorns_dict['store'] = (address.lower(), top_store[1], sort_by_price(top_store_contents), phone, store_type)

    context['unicorns'] = unicorns_dict
    # context['unicorns_json'] = json.dumps(unicorns_json)
    # context['stores_json'] = json.dumps(stores_json)
    return render(request, 'index.html', context)
