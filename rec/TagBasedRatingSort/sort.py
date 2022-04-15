# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: { 基于个性化标签的物品排序推荐算法 }
# @Date: 2022/3/19 16:03
from web.models import *


coursesDict = dict()  # 根据课程类别来保存课程的评分数据
courseEnrollmentDict = dict()  # 根据课程id来保存注册记录
typeEnrollmentDict = dict()  # 根据课程类别来保存注册记录
userEnrollmentDict = dict()  # 根据用户id来保存注册记录


def tagBasedRating(course, typeList):
    """
    :param course: Course 课程
    :param typeList: List 用户学习过的课程的标签集合
    :return: float 课程在标签下的评分
    """
    if course.type in typeList:
        # courses = [course.id for course in Course.objects.filter(type=course.type)]  # 效率太低
        if typeEnrollmentDict.get(course.type, 0) == 0:
            typeEnrollmentDict[course.type] = Enrollment.objects.filter(courseid__in=coursesDict[course.type].keys())
            if coursesDict[course.type].get(course.id, 0) == 0:
                if courseEnrollmentDict.get(course.id, 0) == 0:
                    courseEnrollmentDict[course.id] = typeEnrollmentDict[course.type].filter(courseid=course.id)
                coursesDict[course.type][course.id] = len(courseEnrollmentDict[course.id])/len(typeEnrollmentDict[course.type])
        return coursesDict[course.type][course.id]
    else:
        return 0


def tagPreference(id):
    """
    :param id: int 用户id
    :return: list 标签评分列表
    """
    tagTabVector = [0 for k in range(23)]
    if userEnrollmentDict.get(id, 0) == 0:
        userEnrollmentDict[id] = Enrollment.objects.filter(uid=id)
    for i in range(23):
        if coursesDict.get(i+1, 0) == 0:
            coursesDict[i+1] = dict([(course.id, 0) for course in Course.objects.filter(type=i+1)])  # 用字典保存每个类别的子课程评分字典
        tagTabVector[i] = len(userEnrollmentDict[id].filter(courseid__in=coursesDict[i+1].keys()))
    return [tagTabVector[j]/sum(tagTabVector) for j in range(23)]


def recommendCourseList(uid):
    """
    :param uid: 用户id
    :return: 课程推荐顺序
    """
    userPreferenceVector = tagPreference(uid)
    tList = []
    courseList = []
    for i in range(23):
        if userPreferenceVector[i] > 0:
            tList.append(i + 1)
    for course in Course.objects.filter():
        courseList.append((course.id, tagBasedRating(course, tList)))
    courseList.sort(key=lambda x: x[1], reverse=True)
    return courseList


def getTypeCourse(t):
    if coursesDict.get(t, 0) == 0:
        coursesDict[t] = dict([(course.id, 0) for course in Course.objects.filter(type=t)])
        for course in Course.objects.filter(id__in=coursesDict[t].keys()):
            _ = tagBasedRating(course, [t])
    return sorted(coursesDict[t].items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
