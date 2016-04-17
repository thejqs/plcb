import os, sys
from django.shortcuts import render
from django.views.generic import View
from django.conf import settings
from collections import Counter
import datetime
import re
import json
from operator import itemgetter


# Create your views here.
def unicorns(request):
    context = {}
    d = datetime.date.today()
    # if today's data file doesn't exist, we'll use yesterday's.
    # will help for those cases after midnight and before we havce fresh data
    try:
        f = open(os.path.join(settings.BASE_DIR, 'main/static/unicorns_json/unicorns-{}.json'.format(d)), 'r')
    except IOError:
        f = open(os.path.join(settings.BASE_DIR, 'main/static/unicorns_json/unicorns-{}.json'.format(d - datetime.timedelta(days=1))), 'r')
    j = json.load(f)
    unicorns_dict = {}
    if d.strftime('%Y-%m-%d') in f.name:
        unicorns_dict['data_date'] = d.strftime('%d %B %Y')
    elif (d - datetime.timedelta(days=1)).strftime('%Y-%m-%d') in f:
        unicorns_dict['data-date'] = (d - datetime.timedelta(days=1)).strftime('%d %B %Y')
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

    unicorns_dict['total_unicorns'] = len(j)

    # capturing our various summary data in one loop through the JSON objects
    for unicorn in j:
        name = unicorn['name']
        num_bottles = int(unicorn['bottles'])
        price = float(unicorn['price'])
        on_sale = unicorn['on_sale']
        stores.append(unicorn['store_id'])

        if 'Whiskey' in name:
            whiskey.append(unicorn)
        if 'Bourbon' in name:
            whiskey.append(unicorn)
        if 'Scotch' in name:
            whiskey.append(unicorn)
        if 'Rum' in name:
            rum.append(unicorn)
        if 'Tequila' in name:
            agave.append(unicorn)
        if 'Mezcal' in name:
            agave.append(unicorn)
        if 'Gin' in name and 'Ginjo' not in name:
            gin.append(unicorn)

        if (min_price is None or min_price > price) and price > 1:
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

    unicorns_dict['min'] = [min_name.lower(), '${}'.format(min_price)]
    unicorns_dict['max'] = [max_name.lower(), '${}'.format(max_price)]
    unicorns_dict['bottles'] = [most_bottles_name.lower(), most_bottles, '${}'.format(most_bottles_price), most_bottles_on_sale]
    unicorns_dict['whiskey'] = [len(whiskey), whiskey]
    unicorns_dict['rum'] = [len(rum), rum]
    unicorns_dict['agave'] = [len(agave), agave]
    unicorns_dict['gin'] = [len(gin), gin]

    count_stores = [(x, stores.count(x)) for x in stores]
    top_store = max(count_stores, key=itemgetter(1))
    top_store_contents = [unicorn['name'].lower() for unicorn in j if unicorn['store_id'] == top_store[0]]

    with open('main/static/json/retail_stores-2016-04-10.json', 'r') as f:
        stores_json = json.load(f)
        store_data = None
        for store in stores_json:
            if top_store[0] == store['id']:
                address = store['address']
                phone = store['phone']
                store_type = store['store_type']
            if most_bottles_store_id == store['id']:
                unicorns_dict['bottles'].append(store['address'].lower())
        unicorns_dict['store'] = (address.lower(), top_store[1], top_store_contents, phone, store_type)

    context['unicorns'] = unicorns_dict
    return render(request, 'index.html', context)
