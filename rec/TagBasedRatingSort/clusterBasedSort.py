# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: {基于聚类的课程标签得分排序推荐算法}
# @Date: 2022/4/16 11:27
import time

from web.models import *
from rec.cluster.clusterProcessing import loadCenters
from rec.TagBasedRatingSort.DataProcessing import getSet
from rec.cluster.dataProcessing import *
from rec.cluster.clusterProcessing import getKMeansEstimator


userEnrollmentDict = dict()  # 根据用户id来保存注册记录
TrainSet = getSet('/Users/linshengfeng/学习/大四上/毕业设计/mooc_recommender_system/mooc_back_end/rec/Data/mooc.all.rating.transfer')
TrainSetValues = list(getUserFeatureDict(trainSet=TrainSet).values())
kMeansEstimator = getKMeansEstimator(trainList=TrainSetValues)
userLabels = [int(x) for x in list(kMeansEstimator.predict(TrainSetValues))]
clusterRecDict = dict()  # 根据用户类别存放推荐结果
courseTypeDict = getCourseTypeDict()
Ens = Enrollment.objects.filter()


def getClusterTypeVectorDict():
    # 遍历训练集数据
    typeDict = dict()
    for record in TrainSet:
        if not typeDict.get(userLabels[record[0]], []):
            typeDict[userLabels[record[0]]] = [0 for k in range(23)]
        typeDict[userLabels[record[0]]][courseTypeDict[record[1]] - 1] += 1
    for i in typeDict.keys():
        typeDict[i] = [typeDict[i][j] for j in range(23)]
    return typeDict


clusterTypeDict = getClusterTypeVectorDict()  # 存放每个用户类别与哪些类别课程发生过交互


def getCourseEnrollment():
    courseEnDict = dict()
    for c in courseTypeDict.keys():
        courseEnDict[c] = Ens.filter(courseid=c)
    return courseEnDict


courseEnrollmentDict = getCourseEnrollment()  # 根据课程id来保存注册记录


def tagBasedRating(c):
    """
    :param c: int 课程id
    :return: float 课程在标签下的评分
    """
    return len(courseEnrollmentDict[c])


def tagPreference(id):
    """
    :param id: int 用户id
    :return: list 标签评分列表
    """
    tagTabVector = [0 for k in range(23)]
    if not userEnrollmentDict.get(id, []):
        userEnrollmentDict[id] = Ens.filter(uid=id)
    for en in userEnrollmentDict[id]:
        tagTabVector[courseTypeDict[en.courseid] - 1] += 1
    # 无注册记录
    if sum(tagTabVector) == 0:
        for interest in Intention.objects.filter(uid=id):
            tagTabVector[interest.tid - 1] += 1
    s = sum(tagTabVector)
    # 无兴趣记录
    if s == 0:
        return tagTabVector
    else:
        return [tagTabVector[j]/s for j in range(23)]


def generateRec(t):
    courseList = [(c, len(courseEnrollmentDict[c]) * clusterTypeDict[t][courseTypeDict[c] - 1]) for c in courseTypeDict.keys()]
    courseList.sort(key=lambda x: x[1], reverse=True)
    clusterRecDict[t] = courseList
    return courseList


def recommendCourseList(uid):
    tList = tagPreference(uid)
    ut = int(kMeansEstimator.predict([tList])[0])
    if not clusterRecDict.get(ut, []):
        courseList = generateRec(ut)
    else:
        courseList = clusterRecDict[ut]
    return courseList


def recommendType(courseType):
    courseList = [c.id for c in Course.objects.filter(type=courseType)]
    courseList.sort(key=lambda x: tagBasedRating(x), reverse=True)
    return courseList


def getClusterIntention(uid):
    tList = tagPreference(uid)
    ut = int(kMeansEstimator.predict([tList])[0])
    return clusterTypeDict[ut]