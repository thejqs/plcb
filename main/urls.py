from django.conf.urls import include, url
from django.contrib import admin
from main.views import UnicornView

admin.autodiscover()


urlpatterns = [
    url(r'^$', UnicornView.as_view(), name='unicorns'),
]
