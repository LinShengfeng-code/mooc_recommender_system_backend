# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: {聚类数据处理}
# @Date: 2022/3/28 20:46
import rec.TagBasedRatingSort.DataProcessing as dp
from web.models import *


def getTrainSet():
    return dp.getTrainTest()[0]


def getUserEnrollmentDict(trainSet=None):
    enrollmentDict = dict()
    if not trainSet:
        trainSet = getTrainSet()
    for en in trainSet:
        if enrollmentDict.get(en[0], 0) == 0:
            enrollmentDict[en[0]] = [en[1]]
        else:
            enrollmentDict[en[0]].append(en[1])
    return enrollmentDict


def getCourseTypeDict():
    courseTypeDict = dict()
    for i in range(1302):
        courseTypeDict[i] = Course.objects.get(id=i).type
    return courseTypeDict


def getSingleUserFeatures(courseList, typeDict):
    features = [0 for i in range(23)]
    for c in courseList:
        features[typeDict[c] - 1] += 1
    totalEnrollment = sum(features)
    return [features[i]/totalEnrollment for i in range(len(features))]


def getUserFeatureDict(trainSet=None):
    enrollmentDict = getUserEnrollmentDict(trainSet)
    courseDict = getCourseTypeDict()
    for i in enrollmentDict.keys():
        enrollmentDict[i] = getSingleUserFeatures(enrollmentDict[i], courseDict)
    return enrollmentDict