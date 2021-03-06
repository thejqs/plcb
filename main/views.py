import os, sys
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, requires_csrf_token
from django.views.generic import View
from django.conf import settings
import datetime
from collections import Counter
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

# TODO: find better ways to csrf all post requests while still allowing
# caching on gets. varnish and django cookies -- not so much.
# possible answer: refactoring into function views to decorate more
# granularly and with clearer purpose


class AllUnicornsView(View):
    '''
    handles data and object assembly for the site's primary
    GET request (main page)
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AllUnicornsView, self).dispatch(*args, **kwargs)

    def get(self, request):
        context = {}
        unicorns_dict = {}
        request_context = RequestContext(request)
        form = SearchBoozicornForm()
        context['form'] = form

        # one successful trip to the database, please
        boozicorns = Unicorn.objects.filter(scrape_date=
                                            day_switcher['today'].strftime('%Y-%m-%d'))

        if not boozicorns:
            # get the most recent date for data and use that
            file_date_pattern = '((?<=\-)\d+.*(?=\.))'
            most_recent_unicorns = sorted(os.listdir('main/data/unicorns_json/'))[-1]
            most_recent_file_date = re.search(file_date_pattern, most_recent_unicorns).group()
            boozicorns = Unicorn.objects.filter(scrape_date=most_recent_file_date)
            # unicorns_json = json.load(fp)  # , object_hook=ascii_encode_dict
        most_bottles = None
        stores = []
        whiskey = []
        rum = []
        agave = []
        gin = []
        fancy = []

        sorted_by_price = vh.sort_by_price(boozicorns)

        # capturing as much as we can in one loop through the objects
        for unicorn in boozicorns:
            # name = unicorn.name
            name = unicorn.name
            # num_bottles = int(unicorn.num_bottles)
            num_bottles = int(unicorn.num_bottles)
            num_bottles_unicorn = None
            # price = unicorn.price
            price = unicorn.price
            # we'll count these later to see which store has the most
            # stores.append(unicorn.store.store_id)
            stores.append(unicorn.store.store_id)
            if most_bottles is None or most_bottles < num_bottles:
                most_bottles = num_bottles
                most_bottles_unicorn = unicorn
            if price > 100:
                fancy.append(unicorn)

            if 'whiskey' in name.lower() and unicorn not in whiskey:
                whiskey.append(unicorn)
            elif 'bourbon' in name.lower() and unicorn not in whiskey:
                whiskey.append(unicorn)
            elif 'scotch' in name.lower() and unicorn not in whiskey:
                whiskey.append(unicorn)
            elif ' rum ' in name.lower() or name.endswith('Rum') and unicorn not in rum:
                rum.append(unicorn)
            elif 'tequila' in name.lower() and unicorn not in agave:
                agave.append(unicorn)
            elif 'mezcal' in name.lower() and unicorn not in agave:
                agave.append(unicorn)
            elif (' gin ' in name.lower() or name.endswith('Gin')) and ('Ginjo' not in name and 'Ginger' not in name) and unicorn not in gin:
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

        # could be separate function
        all_prices = [u.price for u in boozicorns]
        most_common_price = Counter(all_prices).most_common()[0]

        median_price = vh.find_median(all_prices)

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


class SearchView(View):
    '''
    handles all search requests, regardless of source page

    requires a cross-site request forgery token which is ignored
    on other pages for caching reasons
    '''
    @method_decorator(requires_csrf_token)
    def dispatch(self, *args, **kwargs):
        return super(SearchView, self).dispatch(*args, **kwargs)

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


class TopStoresView(View):
    '''
    assembles the data for a page displaying the contents of our top 10 stores
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(TopStoresView, self).dispatch(*args, **kwargs)

    def get(self, request):
        context = {}
        unicorns_dict = {}
        request_context = RequestContext(request)

        form = SearchBoozicornForm()
        context['form'] = form
        boozicorns = Unicorn.objects.filter(scrape_date=day_switcher['today'].strftime('%Y-%m-%d'))  # day_switcher['today'].strftime('%Y-%m-%d')
        if not boozicorns:
            try:
                boozicorns = Unicorn.objects.filter(scrape_date=day_switcher['yesterday'].strftime('%Y-%m-%d'))
            except Exception:
                boozicorns = Unicorn.objects.filter(scrape_date=(day_switcher['yesterday'] - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))

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


class FancyView(View):
    '''
    assembles the content for our faniciest unicorns -- those with a retail
    price above $100
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(FancyView, self).dispatch(*args, **kwargs)

    def get(self, request):
        context = {}
        unicorns_dict = {}
        request_context = RequestContext(request)
        form = SearchBoozicornForm()
        context['form'] = form
        boozicorns = Unicorn.objects.filter(scrape_date=day_switcher['today'].strftime('%Y-%m-%d'))  # day_switcher['today'].strftime('%Y-%m-%d')
        if not boozicorns:
            try:
                boozicorns = Unicorn.objects.filter(scrape_date=day_switcher['yesterday'].strftime('%Y-%m-%d'))
            except Exception:
                boozicorns = Unicorn.objects.filter(scrape_date=(day_switcher['yesterday'] - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))

        fancy = [unicorn for unicorn in boozicorns if unicorn.price > 100]
        top_prices = vh.sort_by_price(fancy)

        unicorns_dict['fancy'] = (len(top_prices), top_prices)
        context['unicorns'] = unicorns_dict

        return render(request, 'fancy.html', context, context_instance=request_context)
