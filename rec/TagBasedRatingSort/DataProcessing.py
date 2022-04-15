# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: { 划分数据的模块 }
# @Date: 2022/3/22 13:57
import math

from web.models import *
from django.db.models import Max
from rec.AutoRec.DataProcessing import dataTransform


def getSet(filename):
    fp = open(filename, 'r')
    lines = fp.readlines()
    curSet = []
    for line in lines:
        user, item, _ = line.split('::')
        curSet.append((int(user), int(item)))
    return curSet


def getTrainTest():
    """
    :return: train, test
    """
    return getSet('../Data/mooc.train.rating.transfer'), getSet('../Data/mooc.test.rating.transfer')