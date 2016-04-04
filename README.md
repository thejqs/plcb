Boozicorns
=============
Pennsylvania is a control state when it comes to adult beverages. It hires the administrative and retail employees, it selects the products, it stores and ships them, it controls point-of-sale transactions.

It's generally a terrible system for consumers. We as discerning drinkers have to travel to Ohio or Maryland or wherever for even some basics, some staples. **But it works out OK when one wants a bunch of data about booze.**

Also terrible: the interface(s) the state puts on the data. No joke.

![alt text][finewine]

![alt text][psearch]

I can't search it like I'd want:

- *Do they let me load all search results in one page?* **No.**

- *Do they put store counts in the product results on the search pages?* **No.**

- *Can I query by number of stores a product is in?* **No.**

Oy.

To go through what's provided to me, I'd have to read through roughly 2,500 pages containing about 60,000 products just to find the 14,000-plus that are sold in retail stores. Then I'd have to go through each of those 14,000 to find the ~2,000 that are sold only in one store on a given day.

So somewhere on the order of 17,000 pages to inspect. Daily.

Maybe that's not a lot of data if you're one of those millions-of-rows people, but it's a lot of get requests to a slow and brittle server.

**I guess I should make a computer do it.**

**Good thing I can write code.**

This project exists to collect and illuminate all of the products available for sale in only one store -- one of 597 stores, to be precise -- the state runs across Pennsylvania. The unicorns, as it were. Inspiration came from writing [this story](http://www.post-gazette.com/life/libations/2015/03/04/A-Croatia-to-Pittsburgh-wine-odyssey-How-an-obscure-bottle-gets-in-the-PLCB-system/stories/201503040013) in early 2015, when I didn't have the skills to create this project.

The state's database can do this for us, but the existing interfaces won't allow it. There's no API. Surprise, surprise.  

**So here we are.**

The state's database conveniently updates at the close of business each day, which for some reason means about 5 a.m. the following day. So at least one of the scripts in the project will probably wind up running on a cronjob to collect the data when it's freshest.

Until then: *On Python!* *On JavaScript!*

**Let's do this.**

[finewine]: https://github.com/thejqs/plcb/blob/master/Screenshot%202016-03-22%2010.45.05.png
[psearch]: https://github.com/thejqs/plcb/blob/master/Screenshot%202016-03-22%2010.46.17.png
