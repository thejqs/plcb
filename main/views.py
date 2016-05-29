import os, sys
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.generic import View
from django.conf import settings
from collections import Counter
# import datetime
import json
import re
from operator import itemgetter

from main.models import Store, Unicorn
from main.forms import SearchBoozicornForm
from main.scripts import view_helpers as vh
from project.settings_local import day_switcher

# Create your views here.
# def ascii_encode_dict(data):
#     ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x
#     return dict(map(ascii_encode, pair) for pair in data.items())


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(requires_csrf_token, name='post')
class AllUnicornsView(View):
    '''
    handles data and object assembly for primary GET (main page)
    and POST (search) requests
    '''
    def get(self, request):
        context = {}
        unicorns_dict = {}
        request_context = RequestContext(request)
        form = SearchBoozicornForm()
        context['form'] = form
        # one trip to the database, please
        boozicorns = Unicorn.objects.filter(scrape_date=day_switcher['today'].strftime('%Y-%m-%d'))
        if not boozicorns:
            boozicorns = Unicorn.objects.filter(scrape_date=day_switcher['yesterday'].strftime('%Y-%m-%d'))
        # unicorns_json = json.load(fp)  # , object_hook=ascii_encode_dict
        most_bottles = None
        stores = []
        whiskey = []
        rum = []
        agave = []
        gin = []
        fancy = []

        sorted_by_price = vh.sort_by_price(boozicorns)

        # could be separate function
        all_prices = [u.price for u in boozicorns]
        most_common_price = Counter(all_prices).most_common()[0]

        median_price = vh.find_median(all_prices)

        # capturing as much as we can in one loop through the objects
        for unicorn in boozicorns:
            name = unicorn.name
            num_bottles = int(unicorn.num_bottles)
            num_bottles_unicorn = None
            price = unicorn.price
            # we'll count these later to see which store has the most
            stores.append(unicorn.store.store_id)

            if most_bottles is None or most_bottles < num_bottles:
                most_bottles = num_bottles
                most_bottles_unicorn = unicorn
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
            if 'Gin' in name and 'Ginjo' not in name and 'Ginger' not in name and unicorn not in gin:
                gin.append(unicorn)

        # returns the top 10 store ids
        top_stores = vh.find_top_stores(stores)
        # separates the ids from the number of occurrences;
        # also could be its own function
        top_store_ids = [store[0] for store in top_stores]
        top_store_contents = []
        for idx, store_id in enumerate(top_store_ids):
            contents = boozicorns.filter(store__store_id=store_id)
            top_store_contents.append({(idx, contents[0].store.address.lower().replace(', pa', '')): len(contents)})

        unicorns_dict['num_stores'] = len(Store.objects.filter(store_data_date__gte='2016-05-15'))
        unicorns_dict['top_stores'] = top_store_contents
        # formatted thus to work with a JavaScript function and Ajax call to set the map
        unicorns_dict['scrape_date'] = str(boozicorns[0].scrape_date)
        # formatted thus for display
        unicorns_dict['data_date'] = '{}'.format(boozicorns[0].scrape_date.strftime('%d %B %Y'))
        unicorns_dict['discounted'] = vh.top_10_price_minus_sale_price(boozicorns)
        unicorns_dict['percent_discount'] = vh.top_10_percent_discount(boozicorns)
        unicorns_dict['max'] = sorted_by_price[:10]
        unicorns_dict['min'] = list(reversed([p for p in sorted_by_price if p.bottle_size != 'EACH'][-10:]))
        unicorns_dict['mode'] = most_common_price
        unicorns_dict['median'] = median_price
        unicorns_dict['bottles'] = (most_bottles, most_bottles_unicorn)
        unicorns_dict['whiskey'] = [len(whiskey),
                                    vh.sort_by_price(whiskey)]
        unicorns_dict['rum'] = [len(rum),
                                vh.sort_by_price(rum)]
        unicorns_dict['agave'] = [len(agave),
                                  vh.sort_by_price(agave)]
        unicorns_dict['gin'] = [len(gin),
                                vh.sort_by_price(gin)]
        top_prices = vh.sort_by_price(fancy)
        unicorns_dict['fancy'] = [len(top_prices)]

        context['unicorns'] = unicorns_dict
        return render(request, 'boozicorns.html', context, context_instance=request_context)

    def post(self, request):
        '''
        cleans and handles search input

        returns:
        search response data to the correct template
        '''
        context = {}
        request_context = RequestContext(request)
        form = SearchBoozicornForm(request.POST)
        context['form'] = form

        if form.is_valid():
            context['unicorn_response'] = vh.search_boozicorns(form, context)

            if context['unicorn_response']:
                context['message'] = "WOO BOOZICORNS"
            else:
                context['message'] = 'Ain\'t got none o\' them.'
        else:
            context['message'] = 'That\'s not a valid search.\nC\'mon now.'

        return render_to_response('search_results.html', context, context_instance=RequestContext(request))


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(requires_csrf_token, name='post')
class TopStoresView(View):
    def get(self, request):
        context = {}
        unicorns_dict = {}
        request_context = RequestContext(request)

        form = SearchBoozicornForm()
        context['form'] = form
        boozicorns = Unicorn.objects.filter(scrape_date=day_switcher['today'].strftime('%Y-%m-%d'))
        if not boozicorns:
            boozicorns = Unicorn.objects.filter(scrape_date=day_switcher['yesterday'].strftime('%Y-%m-%d'))

        stores = [unicorn.store.store_id for unicorn in boozicorns]
        # returns the top 10 store ids
        top_stores = vh.find_top_stores(stores)
        # separates the ids from the number of occurrences;
        # also could be its own function
        top_store_ids = [store[0] for store in top_stores]
        top_store_contents = []
        for idx, store_id in enumerate(top_store_ids):
            contents = boozicorns.filter(store__store_id=store_id)
            top_store_contents.append({(idx,
                                        contents[0].store.address.lower().replace(', pa', '')):
                                       (len(contents),
                                        sorted(contents, key=lambda k: k.name))})
        unicorns_dict['store_contents'] = top_store_contents
        context['unicorns'] = unicorns_dict
        context['id_stub'] = 'store-'

        return render(request, 'top_stores.html', context, context_instance=request_context)

    def post(self, request):
        AllUnicornsView(View).post(request)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(requires_csrf_token, name='post')
class FancyView(View):
    def get(self, request):
        context = {}
        unicorns_dict = {}
        request_context = RequestContext(request)
        form = SearchBoozicornForm()
        context['form'] = form
        boozicorns = Unicorn.objects.filter(scrape_date=day_switcher['today'].strftime('%Y-%m-%d'))
        if not boozicorns:
            boozicorns = Unicorn.objects.filter(scrape_date=day_switcher['yesterday'].strftime('%Y-%m-%d'))

        fancy = [unicorn for unicorn in boozicorns if unicorn.price > 100]
        top_prices = vh.sort_by_price(fancy)

        unicorns_dict['fancy'] = (len(top_prices), top_prices)
        context['unicorns'] = unicorns_dict

        return render(request, 'fancy.html', context, context_instance=request_context)

    def post(self, request):
        AllUnicornsView(View).post(request)
