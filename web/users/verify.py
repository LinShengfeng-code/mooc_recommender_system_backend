# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: { 用户相关业务: 校验工具包 }
# @Date: 2022/2/24 8:05 下午
import json, re
import os.path

from utils.error_handler.exceptions import *
from utils.error_handler.enums import *
from web.models import *


# 注册时的数据校验
def verify_register_params(request):
    """
    :param request: 注册请求对象
    :return: response_ret
    """
    # 接受参数
    register_data = json.loads(request.body.decode('utf-8'))
    u_mail = register_data.get('mail', None)
    u_pwd = register_data.get('pwd', None)
    u_pwd_confirm = register_data.get('pwdConfirm', None)
    u_type = register_data.get('type', None)
    u_sid = register_data.get('sid', None)
    u_cid = register_data.get('cid', None)
    u_nick = register_data.get('nick', None)

    # 校验参数
    all_args = [u_mail, u_nick, u_pwd, u_pwd_confirm, u_type, u_sid, u_cid]
    if not all(all_args):
        raise BusinessException(StatusCodeEnum.NECESSARY_PARAMS_ERROR)

    # 用户名 2 - 10 个字符
    if len(u_nick) < 2 or len(u_nick) > 10:
        raise BusinessException(StatusCodeEnum.NICK_LENGTH_ERROR)

    # 用户名重复错误
    if len(User.objects.filter(nick=u_nick)) > 0:
        raise BusinessException(StatusCodeEnum.NICK_REPEAT_ERROR)

    # 邮箱格式错误
    mail_RE = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
    if not re.match(mail_RE, u_mail):
        raise BusinessException(StatusCodeEnum.MAIL_FORMAT_ERROR)

    # 邮箱重复错误
    if len(User.objects.filter(mail=u_mail)) > 0:
        raise BusinessException(StatusCodeEnum.MAIL_REPEAT_ERROR)

    # 密码格式错误
    # 验证用内部函数来实现
    def pwdFormatCheck(pwd):
        upper, lower, num = 0, 0, 0
        for digit in pwd:
            if 'A' <= digit <= 'Z':
                upper += 1
            elif 'a' <= digit <= 'z':
                lower += 1
            elif '0' <= digit <= '9':
                num += 1
            else:
                return False
        if upper == 0 or lower == 0 or num == 0:
            return False
        return True

    if not pwdFormatCheck(u_pwd):
        raise BusinessException(StatusCodeEnum.PWD_FORMAT_ERROR)

    # 确认密码错误
    if u_pwd != u_pwd_confirm:
        raise BusinessException(StatusCodeEnum.PWD_CONFIRM_ERROR)


# 登录时的数据校验
def verify_login_params(request):
    """
    :param request: 登录请求对象
    :return: response_ret
    """
    # 接收参数
    login_data = json.loads(request.body.decode('utf-8'))
    u_mail = login_data.get('mail', None)
    u_pwd = login_data.get('pwd', None)
    # 校验参数
    all_args = [u_mail, u_pwd]
    if not all(all_args):
        raise BusinessException(StatusCodeEnum.NECESSARY_PARAMS_ERROR)

    # 用户名不存在错误
    if len(User.objects.filter(mail=u_mail)) == 0:
        raise BusinessException(StatusCodeEnum.MAIL_NOT_EXIST_ERROR)

    # 密码错误
    assert isinstance(User.objects.get(mail=u_mail).password, object)
    if not u_pwd == User.objects.get(mail=u_mail).password:
        raise BusinessException(StatusCodeEnum.PWD_ERROR)


# 头像验证
def verify_image(request):
    img = request.FILES.get('avatar', None)
    if img is None:
        raise BusinessException(StatusCodeEnum.AVATAR_MISS_ERROR)
    if img.size > 2 * 1024 * 1024:
        raise BusinessException(StatusCodeEnum.AVATAR_LARGE_ERROR)
    if os.path.splitext(img.name)[-1].lower() != '.jpg':
        raise BusinessException(StatusCodeEnum.AVATAR_SUFFIX_ERROR)
    return img