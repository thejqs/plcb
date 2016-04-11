import os, sys
from django.shortcuts import render
from django.views.generic import View
from django.conf import settings
from collections import Counter
import csv
import json
from operator import itemgetter

# Create your views here.
def unicorns(request):
    context = {}
    unicorns_csv = csv.reader(open(os.path.join(settings.BASE_DIR, 'main/unicorns_csv/unicorns-2016-04-07.csv'), 'r'))
    next(unicorns_csv, None)
    max_price = None
    min_price = None
    most_bottles = None
    min_name = None
    max_name = None
    bottles_name = None
    stores = []

    unicorns_dict = {}

    for row in unicorns_csv:
        num_bottles = int(row[1])
        name = row[2]
        price = float(row[4])
        store = row[7]
        stores.append(store)

        if (min_price == None or min_price > price) and price > 1:
            min_price = price
            min_name = name
        if max_price == None or max_price < price:
            max_price = price
            max_name = name
        if most_bottles == None or most_bottles < num_bottles:
            most_bottles = num_bottles
            bottles_name = name

    unicorns_dict['min'] = (min_name.lower(), '${}'.format(min_price))
    unicorns_dict['max'] = (max_name.lower(), '${}'.format(max_price))
    unicorns_dict['bottles'] = (bottles_name.lower(), most_bottles)

    count_stores = [(x, stores.count(x)) for x in stores]

    top_store = max(count_stores, key=itemgetter(1))

    with open('main/static/json/stores.json', 'r') as f:
        stores_json = json.load(f)
        store_data = None
        for store in stores_json:
            if top_store[0] == store['id']:
                store_data = store['address']
        unicorns_dict['store'] = (store_data.lower(), top_store[1])

    context['unicorns'] = unicorns_dict
    return render(request, 'index.html', context)
