# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: { 把课程的图片地址同步到数据库 }
# @Date: 2022/3/11 2:34 下午
from mooc_back_end.settings import MEDIA_ROOT
from web.models import *
import hashlib, os


if __name__ == '__main__':
    for i in range(0, 1302):
        if os.path.exists(MEDIA_ROOT + 'web/img/class/' + str(i) + '.jpg'):
            course = Course.objects.get(id=i)
            course.img = 'web/img/class/' + str(i) + '.jpg'
            course.save()
