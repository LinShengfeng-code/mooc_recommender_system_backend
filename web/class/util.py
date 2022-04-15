# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: { 课程相关的工具函数 }
# @Date: 2022/3/11 2:03 下午
from web.models import *
from django.http import JsonResponse
from rec.AutoRec.RunAutoRec import getAutoRecModel
import numpy as np
from rec.ItemBasedCollaborativeFilter.itemBasedCF import itemBasedCF
from rec.TagBasedRatingSort.DataProcessing import getTrainTest


def getUserRatingVector(uid=None):
    v = [0 for i in range(1302)]
    if uid:
        enrollment = Enrollment.objects.filter(uid=uid)
        for en in enrollment:
            if 0 <= en.courseid < 1302:
                v[en.courseid] = 5
    return v


def getRecommendIds(uid=None):
    autoRecModel = getAutoRecModel()
    result = autoRecModel.recommend_user(np.array(getUserRatingVector(uid)), 5)
    return result


def getCourseInfo(cid):
    """
    :param cid: 课程编号
    :return: 课程信息的Json对象
    """
    def getAudience(cid):
        """
        :param cid: 课程编号
        :return: 注册学习人数
        """
        return len(Enrollment.objects.filter(courseid=cid))

    def getImgUrl(course):
        """
        :param course: 课程对象
        :return: 课程图片地址
        """
        if str(course.img) != '':
            return 'http://localhost:8000/media/' + str(course.img)
        else:
            return 'http://localhost:8000/media/web/img/class/default.jpg'

    def getSchoolTeacherName(course):
        """
        :param course: 课程对象
        :return: 开课老师昵称, 开课学校名称
        """
        t = Teacher.objects.get(uid=course.tid)
        return User.objects.get(uid=t.uid).nick, School.objects.get(sid=t.sid).sname

    def getTime(course):
        return course.time

    course = Course.objects.get(id=cid)
    teacherNick, schoolName = getSchoolTeacherName(course)
    return {'id': course.id, 'name': course.name, 'time': getTime(course), 'abstract': course.abstract, 'teacher': teacherNick, 'school': schoolName, 'imgUrl': getImgUrl(course), 'audience': getAudience(cid)}


def getTypes():
    types = CourseType.objects.filter()
    typeList = []
    for t in types:
        typeList.append({'index': t.id, 'name': t.name})
    return typeList


def setUserInfoInComment(comment):
    leftUser = User.objects.get(uid=comment['uid'])
    comment['avatarUrl'] = str(leftUser.avatar)
    comment['nick'] = leftUser.nick
    return comment


def transferEnrollments():
    curSet = []
    for en in Enrollment.objects.filter():
        curSet.append((en.uid, en.courseid))
    return curSet


# itemCF的对象
itemCF = itemBasedCF(trainSet=transferEnrollments(), testSet=None)


# 相关推荐
def relativeRecommend(cid):
    return itemCF.recommendBasedOnItem(cid)