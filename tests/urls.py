from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponse


urlpatterns = [
    url(r'^$', lambda request, *args, **kwargs: HttpResponse()),
    url(r'^admin/', admin.site.urls),
]
