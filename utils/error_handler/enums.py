# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: { 项目枚举类模块 }
# @Date: 2022/2/24 3:35 下午

from enum import Enum


class StatusCodeEnum(Enum):
    """状态码枚举类"""

    OK = (0, '成功')
    ERROR = (-1, '错误')
    SERVER_ERR = (500, '服务器异常')
    # 登录注册模块错误
    MAIL_FORMAT_ERROR = (4001, '邮箱格式错误')
    MAIL_REPEAT_ERROR = (4002, '邮箱已被注册')
    MAIL_NOT_EXIST_ERROR = (4003, '未注册邮箱')
    NICK_REPEAT_ERROR = (4004, '昵称已被注册')
    NICK_LENGTH_ERROR = (4005, '昵称长度过短或过长')
    PWD_ERROR = (4006, '密码错误')
    PWD_FORMAT_ERROR = (4007, '密码不规范')
    PWD_CONFIRM_ERROR = (4008, '密码不一致')
    NECESSARY_PARAMS_ERROR = (4009, '缺少必填信息')
    AVATAR_MISS_ERROR = (4010, '未提供头像')
    AVATAR_LARGE_ERROR = (4011, '头像大小仅支持2MB及以下')
    AVATAR_SUFFIX_ERROR = (4012, '头像格式仅支持jpg!')
    USER_NOT_EXIST_ERROR = (4013, '用户不存在!')
    QUERY_NOT_EXIST_ERROR = (4014, '请求参数错误!')
    CLASS_NAME_REPEAT = (4015, '课程名称重复')
    # 其他错误
    DB_ERR = (5000, '数据库错误')
    PARAM_ERROR = (5001, '参数错误')

    @property
    def code(self):
        """
        :return: 状态码
        """
        return self.value[0]

    @property
    def errmsg(self):
        """
        :return: 错误信息
        """
        return self.value[1]
