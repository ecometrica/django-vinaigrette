from django.urls import re_path
from django.contrib import admin
from django.http import HttpResponse


urlpatterns = [
    re_path(r'^$', lambda request, *args, **kwargs: HttpResponse()),
    re_path(r'^admin/', admin.site.urls),
]
