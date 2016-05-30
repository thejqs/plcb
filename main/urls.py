from django.conf.urls import include, url
from django.contrib import admin
from main.views import AllUnicornsView, TopStoresView, FancyView, SearchView

admin.autodiscover()


urlpatterns = [
    url(r'^$', AllUnicornsView.as_view(), name='unicorns'),
    url(r'^search/$', SearchView.as_view(), name='search'),
    url(r'^top-stores/$', TopStoresView.as_view(), name='stores'),
    url(r'^fancy/$', FancyView.as_view(), name='fancy'),
]
