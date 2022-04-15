# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: { Token相关工具包 }
# @Date: 2022/2/27 9:39 下午

import time
from django.core import signing
import hashlib
from django.core.cache import cache

HEADER = {'typ': 'JWP', 'alg': 'default'}
KEY = 'LIN_SHENG_FENG'
SALT = 'go_mooc'
TIME_OUT = 30 * 60  # 30分钟


def encrypt(plain_text):
    """
    加密函数
    :param plain_text: 明文
    :return: 密文
    """
    value = signing.dumps(plain_text, key=KEY, salt=SALT)
    value = signing.b64_encode(value.encode()).decode()
    return value


def decrypt(src):
    """
    解密函数
    :param src: 密文
    :return: 明文
    """
    src = signing.b64_decode(src.encode()).decode()
    raw = signing.loads(src, key=KEY, salt=SALT)
    print(type(raw))
    return raw


def create_token(nick):
    """
    根据昵称产生token
    :param nick: 昵称
    :return: token
    """
    # 1. 加密头部信息
    header = encrypt(HEADER)
    # 2. 构造payload
    payload = {'nick': nick, 'iat': time.time()}
    payload = encrypt(payload)
    # 3. 生成签名
    md5 = hashlib.md5()
    md5.update(("%s.%s" % (header, payload)).encode())
    signature = md5.hexdigest()
    token = "%s.%s.%s" % (header, payload, signature)
    # 保存到缓存
    cache.set(nick, token, TIME_OUT)
    return token


def get_payload(token):
    payload = str(token).split('.')[1]
    payload = decrypt(payload)
    return payload


def get_nick(token):
    payload = get_payload(token)
    return payload['nick']


def check_token(token):
    nick = get_nick(token)
    last_token = cache.get(nick)
    if last_token:
        return last_token == token
    return False
