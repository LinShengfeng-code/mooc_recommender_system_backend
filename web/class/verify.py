# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: { 课程模块 验证 }
# @Date: 2022/3/20 17:15
import json

from web.models import *
from utils.error_handler.exceptions import *
from utils.error_handler.enums import *


def verify_recommends_params(uid, start, t):
    if len(User.objects.filter(uid=uid)) == 0 and uid > 0:
        raise BusinessException(StatusCodeEnum.USER_NOT_EXIST_ERROR)
    if start < 0 or start >= len(Course.objects.filter()) or start % 20:
        raise BusinessException(StatusCodeEnum.QUERY_NOT_EXIST_ERROR)
    if not 0 <= t <= 23:
        raise BusinessException(StatusCodeEnum.QUERY_NOT_EXIST_ERROR)


def verify_class_params(request):
    class_data = request.POST
    print(class_data)
    c_name = class_data.get('name', None)
    c_type = class_data.get('type', None)
    tid = class_data.get('tid', None)
    all_args = [c_name, c_type, tid]
    if not all(all_args):
        raise BusinessException(StatusCodeEnum.NECESSARY_PARAMS_ERROR)
    if len(Course.objects.filter(name=c_name)):
        raise BusinessException(StatusCodeEnum.CLASS_NAME_REPEAT)
    if not 1 <= int(c_type) <= 23:
        raise BusinessException(StatusCodeEnum.QUERY_NOT_EXIST_ERROR)
    return request