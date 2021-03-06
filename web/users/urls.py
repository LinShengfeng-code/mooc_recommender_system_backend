# -*- coding: utf-8 -*-
from django.conf.urls import url

from web.users.views import *

urlpatterns = [
    url("show_schools", show_schools),
    url("show_colleges", show_colleges),
    url("mail_repeat", mail_repeat),
    url("nick_repeat", nick_repeat),
    url("add_new_user", add_new_user),
    url("log_in", log_in),
    url(r'^update_avatar/(\d+)', update_avatar),
    url('get_hobbies', hobbies),
    url('get_school_college', schoolCollege),
    url('interests', interests),
    url('modify_intentions', modifyIntentions)
]
