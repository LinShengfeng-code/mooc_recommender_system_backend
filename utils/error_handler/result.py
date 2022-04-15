# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: { 项目信息返回结果模块 }
# @Date: 2022/2/24 3:34 下午

from .enums import StatusCodeEnum


class R(object):
    """
    统一项目信息返回结果类
    """

    def __init__(self):
        self.code = None
        self.errmsg = None
        self._data = dict()

    @staticmethod
    def ok():
        """
        组织成功响应信息
        :return:
        """
        r = R()
        r.code = StatusCodeEnum.OK.code
        r.errmsg = StatusCodeEnum.OK.errmsg
        return r

    @staticmethod
    def error():
        """
        组织错误响应信息
        :return:
        """
        r = R()
        r.code = StatusCodeEnum.ERROR.code
        r.errmsg = StatusCodeEnum.ERROR.errmsg
        return r

    @staticmethod
    def server_error():
        """
        组织服务器错误信息
        :return:
        """
        r = R()
        r.code = StatusCodeEnum.SERVER_ERR.code
        r.errmsg = StatusCodeEnum.SERVER_ERR.errmsg
        return r

    @staticmethod
    def set_result(enum):
        """
        组织对应枚举类的响应信息
        :param enum: 状态枚举类
        :return:
        """
        r = R()
        r.code = enum.code
        r.errmsg = enum.errmsg
        return r

    def data(self, key=None, obj=None):
        """统一后端返回的数据"""

        if key:
            self._data[key] = obj

        context = {
            'code': self.code,
            'errmsg': self.errmsg,
            'data': self._data
        }
        return context
