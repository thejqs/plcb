<img src="https://github.com/thejqs/plcb/blob/master/main/static/media/boozicorn_transparent.png" width="350"  />

#Boozicorns#

There was this wine. The only store in Pennsylvania that carried it was 60 miles away.

I knew this because Pennsylvania is a control state when it comes to adult beverages. It hires the administrative and retail employees, it selects the products, it stores and ships them, it controls point-of-sale transactions. If you know specifically what you want, it's relatively easy to search for it.

But not everyone does. And the Pennsylvania Liquor Control Board's search interfaces are -- let's go with "not good."

I can't search like I'd want:

- *Do they let me load all search results in one page?* **No.**

- *Do they put store counts in the product results on the search pages?* **No.**

- *Can I query by number of stores a product is in?* **No.**

Oy.

**The data, however, is there.**

This project exists to collect and illuminate all of the products available for sale in only one store of the hundreds the PLCB runs across the commonwealth. The unicorns, as it were. **The boozicorns.**

This kind of data isn't available in every state. That's part of the fun here. Pennsylvania's weirdness allows us to explore something we otherwise couldn't.

It's generally a terrible system for consumers. We as discerning drinkers have to travel to Ohio or Maryland or wherever for even some basics, some staples. **But it works out OK when one wants a bunch of data about booze.**

Searching for that one wine turned into [this story](http://www.post-gazette.com/life/libations/2015/03/04/A-Croatia-to-Pittsburgh-wine-odyssey-How-an-obscure-bottle-gets-in-the-PLCB-system/stories/201503040013) in early 2015, when I didn't yet have the skills to create this project.

To go through those existing interfaces -- they [really](https://github.com/thejqs/plcb/blob/master/Screenshot%202016-03-22%2010.46.17.png) are [special](https://github.com/thejqs/plcb/blob/master/interface.png) -- I'd have to read through roughly 2,500 search pages containing about 60,000 products or comb 680 pages of ugly PDF just to find the 14,000-plus that are sold in retail stores. Then I'd have to go through each of those 14,000 to find the ~2,000 that are sold only in one store on a given day.

So somewhere on the order of 14,000 to 17,000 pages to inspect. Daily.

Maybe that's not a lot of data if you're one of those millions-of-rows people, but it's a lot of get requests to a slow and brittle server.

And it's a lot to ask of any human. **I guess I should make a computer do it.**


###data liberation###
There's no API. Surprise, surprise. So a-scraping we go.

That doesn't mean we can't be nice about how we go about acquiring what we want. I send my name and email address in headers and limit concurrent requests to the PLCB's server(s). **This is data that can help people be better consumers.** Liberating data from hard-to-navigate interfaces can only help the PLCB's customers. Or at least that's what I'm telling myself.

And it's not like the PLCB is actively discouraging this sort of thing.

![alt text][permissions]

So here we are.

```python
unicorns = []
for tree in trees:
    is_unicorn = check_for_unicorn(tree)
    # just being explicit about our False case
    if not is_unicorn:
        continue
    else:
        unicorn = assemble_unicorn(tree)
        sale_price = on_sale(tree)
        # it's either this or a ternary operator, so ....
        try:
            unicorn['on_sale'] = float(sale_price.replace('Sale Price: $', ''))
        except (ValueError, AttributeError) as e:
            unicorn['on_sale'] = False
        unicorns.append(unicorn)
return unicorns
```

The first, synchronous version of this scraper took eight hours for those 17,000 gets. Multiprocessing got it to about three and a half hours. Now with the PDF parser it's down to about an hour and 15 minutes running with plenty of memory, or about an hour and a half with an optimized number of pool workers in a more-constrained environment.

That time savings came with a price: a dramatically CPU- and memory-intensive `load()` operation for the PDF, courtesy of a library sub-module. But the tradeoff seemed worth it.

Once in hand, the data goes into a PostgreSQL database for later time-series and pattern analysis and also up to an S3 instance as a daily JSON file to support an Ajax call to make our map.

**Isn't that better?**

![alt text][leaflet]

The state's database conveniently updates at the close of business each day, which for some reason means about 5 a.m. or later the following day. The PDF doesn't go up until about 8 a.m. at the earliest. On Sundays and other random days it can be 2 p.m. or later -- sometimes even 8 p.m.

A daily cronjob set up on a a remote Linux/Ubuntu server runs a shell script that handles the scraper to collect the data when it's freshest as well as restarting server processes whenever the scraper completes. Varnish and its fat TTL steps between Apache and the request to handle caching as the data doesn't change more than once a day. How well does Varnish play with Django's cross-site forgery request tokens, you ask?

![alt text][puking_rainbows]

The data itself might not change much day to day. Maybe something is on sale today that wasn't yesterday. Or the number of bottles available might have gone down from 12 one day to eight the next to two the next.

Guess there's really only one way to find out.

Thus: *On Python!* *On JavaScript!*

**Let's do this.**

[leaflet]:https://github.com/thejqs/plcb/blob/master/leaflet_screenshot1.png
[permissions]: https://github.com/thejqs/plcb/blob/master/permissions.png
[puking_rainbows]: https://github.com/thejqs/plcb/blob/master/main/static/media/puking_rainbows.gif
