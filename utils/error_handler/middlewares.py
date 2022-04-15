# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: { 项目中间件模块 }
# @Date: 2022/2/24 3:24 下午
import logging

from django.db import DatabaseError
from django.http.response import JsonResponse
from django.http import HttpResponseServerError
from django.middleware.common import MiddlewareMixin

from .result import R
from .enums import StatusCodeEnum
from .exceptions import BusinessException


logger = logging.getLogger('django')


class ExceptionMiddleWare(MiddlewareMixin):
    """统一异常处理中间件"""

    def process_exception(self, request, exception):
        """
        :param request: 请求对象
        :param exception: 异常对象
        :return:
        """
        if isinstance(exception, BusinessException):
            # 业务异常处理
            data = R.set_result(exception.enum_cls).data()
            return JsonResponse(data)

        elif isinstance(exception, DatabaseError):
            # 数据库异常
            r = R.set_result(StatusCodeEnum.DB_ERR)
            logger.error(r.data(), exc_info=True)
            return HttpResponseServerError(StatusCodeEnum.SERVER_ERR.errmsg)

        elif isinstance(exception, Exception):
            # 服务器异常处理
            r = R.server_error()
            logger.error(r.data(), exc_info=True)
            return HttpResponseServerError(r.errmsg)

        return None
