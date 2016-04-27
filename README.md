<img src="https://github.com/thejqs/plcb/blob/master/main/static/media/boozicorn_transparent.png" width="250" />

Pennsylvania is a control state when it comes to adult beverages. It hires the administrative and retail employees, it selects the products, it stores and ships them, it controls point-of-sale transactions.

It's generally a terrible system for consumers. We as discerning drinkers have to travel to Ohio or Maryland or wherever for even some basics, some staples. **But it works out OK when one wants a bunch of data about booze.**

Also terrible: the interface(s) the state puts on the data. No joke.

![alt text][finewine]

![alt text][psearch]

I can't search like I'd want:

- *Do they let me load all search results in one page?* **No.**

- *Do they put store counts in the product results on the search pages?* **No.**

- *Can I query by number of stores a product is in?* **No.**

Oy.

To go through what's provided to me, I'd have to read through roughly 2,500 search pages containing about 60,000 products or comb 680 pages of ugly PDF just to find the 14,000-plus that are sold in retail stores. Then I'd have to go through each of those 14,000 to find the ~2,000 that are sold only in one store on a given day.

So somewhere on the order of 14,000 to 17,000 pages to inspect. Daily.

Maybe that's not a lot of data if you're one of those millions-of-rows people, but it's a lot of get requests to a slow and brittle server.

**I guess I should make a computer do it.**

**Good thing I can write code.**

This project exists to collect and illuminate all of the products available for sale in only one store -- one of 597 stores, to be precise -- the state runs across Pennsylvania. The unicorns, as it were. **The boozicorns.** Inspiration came from writing [this story](http://www.post-gazette.com/life/libations/2015/03/04/A-Croatia-to-Pittsburgh-wine-odyssey-How-an-obscure-bottle-gets-in-the-PLCB-system/stories/201503040013) in early 2015, when I didn't yet have the skills to create this project.

The state's database can do this for us, but the existing interfaces won't allow it. There's no API. Surprise, surprise.

That doesn't mean we can't be nice about it. I send my name and email address in headers and limit concurrent requests to the PLCB's server(s). **This project exists to help people be better consumers.** Liberating data from hard-to-navigate interfaces can only help the PLCB's customers. Or at least that's what I'm telling myself.

And it's not like the PLCB is actively discouraging this sort of thing.

![alt text][permissions]

So here we are.

**Isn't that better?**

![alt text][leaflet]

The state's database conveniently updates at the close of business each day, which for some reason means about 5 a.m. or later the following day. On Sundays it can be almost 2 p.m. So at least one of the scripts in the project will probably wind up running on a cronjob to collect the data when it's freshest.

And the data might not change much day to day. But maybe something is on sale today that wasn't yesterday. Or the number of bottles available might have gone down from 12 one day to eight the next to two the next.

Guess there's really only one way to find out.

Thus: *On Python!* *On JavaScript!*

**Let's do this.**

[boozicorn]:<img src="https://github.com/thejqs/plcb/blob/master/main/static/media/boozicorn_transparent.png" width="250" />
[leaflet]:https://github.com/thejqs/plcb/blob/master/leaflet_screenshot1.png
[finewine]: https://github.com/thejqs/plcb/blob/master/Screenshot%202016-03-22%2010.46.17.png
[psearch]: https://github.com/thejqs/plcb/blob/master/interface.png
[permissions]: https://github.com/thejqs/plcb/blob/master/permissions.png
