import os, sys
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.conf import settings
from collections import Counter
import datetime
import json
import re
from operator import itemgetter

from main.models import Store, Unicorn
from main.forms import SearchBoozicornForm


# Create your views here.
# def ascii_encode_dict(data):
#     ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x
#     return dict(map(ascii_encode, pair) for pair in data.items())

today = datetime.date.today()
yesterday = (today - datetime.timedelta(days=1))


class UnicornView(View):
    '''
    handles data and object assembly for GET and POST requests
    '''

    # TODO: pull out these helper functions into a separate file. they
    # inform the view but are not themselves views
    def find_median(self, lst):
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

    def sort_by_price(self, lst):
        '''
        a one-liner, but one we'll use repeatedly.
        would otherwise be a lambda

        Args:
        a list of dictionaries, which each contain 'price' keys
        '''
        return sorted(lst, key=lambda k: k.price, reverse=True)

    def find_top_stores(self, lst):
        '''
        given a list, finds the number of occurrences of each item, returning
        the most-common value
        '''
        return Counter(lst).most_common(10)
        # return max([(x, lst.count(x)) for x in lst], key=itemgetter(1))

    def top_10_price_minus_sale_price(self, lst_of_objs):
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

    def top_10_percent_discount(self, lst_of_objs):
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


    def get(self, request):
        context = {}
        unicorns_dict = {}
        form = SearchBoozicornForm()
        context['form'] = form
        boozicorns = Unicorn.objects.filter(scrape_date=today.strftime('%Y-%m-%d'))
        if not boozicorns:
            boozicorns = Unicorn.objects.filter(scrape_date=yesterday.strftime('%Y-%m-%d'))
        # unicorns_json = json.load(fp)  # , object_hook=ascii_encode_dict
        max_price = None
        min_price = None
        min_name = None
        max_name = None
        most_bottles = None
        most_bottles_price = None
        most_bottles_on_sale = None
        most_bottles_name = None
        most_bottles_store = None
        stores = []
        whiskey = []
        rum = []
        agave = []
        gin = []
        fancy = []

        sorted_by_price = self.sort_by_price(boozicorns)

        # could be separate function
        all_prices = [u.price for u in boozicorns]
        most_common_price = Counter(all_prices).most_common()[0]

        median_price = self.find_median(all_prices)

        # capturing various summary data in one loop through the JSON objects
        for unicorn in boozicorns:
            name = unicorn.name
            num_bottles = int(unicorn.num_bottles)
            price = unicorn.price
            on_sale = unicorn.on_sale_price
            # we'll count these later to see which store has the most
            stores.append(unicorn.store.store_id)

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
            # excluding 'Ginger' and 'Ginjo'
            if 'Gin' in name and 'Ginjo' not in name and 'Ginger' not in name and unicorn not in gin:
                gin.append(unicorn)

            # if (min_price is None or min_price > price) and price > 1 and unicorn.bottle_size != 'EACH':
            #     min_price = price
            #     min_name = name
            if most_bottles is None or most_bottles < num_bottles:
                most_bottles = num_bottles
                most_bottles_name = name
                most_bottles_price = price
                most_bottles_on_sale = 'Sale price: ${}'.format(unicorn.on_sale_price) if unicorn.on_sale_price else None
                most_bottles_store = unicorn.store

        # gives me the top 10 store ids
        top_stores = self.find_top_stores(stores)
        # separates the ids from the number of occurrences
        # also could be its own function
        top_store_ids = [store[0] for store in top_stores]
        top_store_contents = []
        for store_id in top_store_ids:
            contents = boozicorns.filter(store__store_id=store_id)
            top_store_contents.append({contents[0].store.address: (len(contents),
                                                                   contents)})

        unicorns_dict['top_stores'] = top_store_contents
        # formatted thus to work with a JavaScript function and Ajax call to set the map
        unicorns_dict['scrape_date'] = str(boozicorns[0].scrape_date)
        # formatted thus for display
        unicorns_dict['data_date'] = '{}'.format(boozicorns[0].scrape_date.strftime('%d %B %Y'))
        unicorns_dict['discounted'] = self.top_10_price_minus_sale_price(boozicorns)
        unicorns_dict['percent_discount'] = self.top_10_percent_discount(boozicorns)
        unicorns_dict['min'] = sorted_by_price[-10:]
        unicorns_dict['mode'] = most_common_price
        unicorns_dict['median'] = median_price
        unicorns_dict['bottles'] = [most_bottles_name.lower(),
                                    most_bottles,
                                    '${}'.format(most_bottles_price),
                                    most_bottles_on_sale,
                                    most_bottles_store]
        unicorns_dict['whiskey'] = [len(whiskey),
                                    self.sort_by_price(whiskey)]
        unicorns_dict['rum'] = [len(rum),
                                self.sort_by_price(rum)]
        unicorns_dict['agave'] = [len(agave),
                                  self.sort_by_price(agave)]
        unicorns_dict['gin'] = [len(gin),
                                self.sort_by_price(gin)]
        top_prices = self.sort_by_price(fancy)
        unicorns_dict['fancy'] = [len(fancy),
                                  top_prices]
        unicorns_dict['max'] = top_prices[:10]

        context['unicorns'] = unicorns_dict
        return render(request, 'boozicorns.html', context)

    def post(self, request):
        context = {}
        form = SearchBoozicornForm(request.POST)
        context['form'] = form

        if form.is_valid():
            search = form.cleaned_data['name'].strip()
            if search.isalnum():
                response = Unicorn.objects.filter(name__icontains=search).filter(scrape_date=today.strftime('%Y-%m-%d'))
                clean_response = [r for r in response for m in [re.search(r'(?<=\b)({0}\b)'.format(search.lower()), r.name.lower())] if m]
                context['unicorn_response'] = clean_response
                if not context['unicorn_response']:
                    response = Unicorn.objects.filter(name__icontains=search).filter(scrape_date=yesterday.strftime('%Y-%m-%d'))
                    clean_response = [r for r in response for m in [re.search(r'(?<=\b)({0}\b)'.format(search.lower()), r.name.lower())] if m]
                    context['unicorn_response'] = clean_response
                if context['unicorn_response']:
                    context['message'] = "WOO BOOZICORNS"
                else:
                    context['message'] = 'Ain\'t got none o\' them.'
            else:
                context['message'] = 'That\'s not a valid search.\nC\'mon now.'
        else:
            context['message'] = 'That\'s not a valid search. C\'mon now.'

        return render_to_response('search_results.html', context, context_instance=RequestContext(request))
