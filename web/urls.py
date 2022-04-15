# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.urls import path, include


urlpatterns = [
    url("users/", include('web.users.urls'), ),
    url("class/", include('web.class.urls'), ),
]
