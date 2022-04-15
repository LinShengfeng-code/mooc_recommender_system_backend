# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: { 课程相关的业务 }
# @Date: 2022/3/4 9:48 下午
from django.views.decorators.http import require_http_methods
from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rec.TagBasedRatingSort.sort import recommendCourseList, getTypeCourse
from django.db.models import Max
from .verify import *
import datetime

from .util import *


# 获取经典推荐
@require_http_methods(["GET"])
def getRecommendCourses(request):
    response = {}
    courseList = []
    """
    先随机生成推荐序列
    """
    if request.GET.get('uid', -1) != -1:
        recommendCourseIds = getRecommendIds(uid=int(request.GET['uid']))
    else:
        recommendCourseIds = getRecommendIds()
    for i in recommendCourseIds:
        courseList.append(getCourseInfo(i))
    response['courseList'] = courseList
    return JsonResponse(response)


# 根据课程id获取课程信息
@require_http_methods(['GET'])
def getSingleCourseInfo(request, courseid):
    return JsonResponse({'course': getCourseInfo(courseid)})


# 获取所有的课程类别
@require_http_methods(['GET'])
def getAllTypes(request):
    return JsonResponse({'typeList': getTypes()})


# 获取全部推荐课程
userCourseList = dict()  # 把请求过的用户的结果保存下来, 但这种用变量存储的方式不仅危险，而且不易于更新，基本上相当于定死了
allTypeList = dict()


@require_http_methods(['GET'])
def getAllRecommends(request, uid, start, t):
    verify_recommends_params(int(uid), int(start), int(t))
    courseList = []
    if int(t) == 0:
        if userCourseList.get(uid, 0) == 0:
            userCourseList[uid] = recommendCourseList(int(uid))
        for i in range(int(start), min(int(start) + 20, len(userCourseList[uid]))):
            courseList.append(getCourseInfo(userCourseList[uid][i][0]))
        return JsonResponse({'courseList': courseList, 'total': len(userCourseList[uid])})
    else:
        if allTypeList.get(int(t), 0) == 0:
            allTypeList[t] = getTypeCourse(int(t))
        for i in range(int(start), min(int(start) + 20, len(allTypeList[t]))):
            courseList.append(getCourseInfo(allTypeList[t][i][0]))
        return JsonResponse({'courseList': courseList, 'total': len(allTypeList[t])})


@csrf_exempt
@require_http_methods(['POST'])
def createClass(request):
    class_data, request = verify_class_params(request)
    c = Course(id=Course.objects.latest('id').id + 1, type=int(class_data['type']), name=class_data['name'],
               abstract=class_data['abstract'] if class_data['abstract'] == '' else None, tid=int(class_data['tid']),
               time=datetime.datetime.now(), link=class_data['link'] if class_data['link'] != '' else None)
    c.save()
    courseImgFile = request.FILES.get('courseImgFile', None)
    if courseImgFile is not None:
        courseImgFile.name = str(c.id) + '.jpg'
        c.img = courseImgFile
        c.save()
    return JsonResponse({'respMsg': '课程上传成功', 'respCode': '200'})


@require_http_methods(['GET'])
def validClassName(request):
    result = True
    if len(Course.objects.filter(name=request.GET['name'])):
        result = False
    return JsonResponse({'respMsg': result, 'respCode': '200'})


teacherCourseDict = dict()


@require_http_methods(['GET'])
def getTeacherCourse(request):
    tid = int(request.GET['tid'])
    start = int(request.GET['start'])
    if teacherCourseDict.get(tid, 0) == 0:
        teacherCourseDict[tid] = [c.id for c in Course.objects.filter(tid=tid)]
    return JsonResponse({'courseList': [getCourseInfo(teacherCourseDict[tid][i]) for i in range(start, min(len(teacherCourseDict[tid]), start + 20))], 'total': len(teacherCourseDict[tid])})


userCourseDict = dict()


@require_http_methods(['GET'])
def getUserRegisterCourse(request):
    uid = int(request.GET['uid'])
    start = int(request.GET['start'])
    if userCourseDict.get(uid, 0) == 0:
        userCourseDict[uid] = [c.courseid for c in Enrollment.objects.filter(uid=uid)]
    return JsonResponse({'courseList': [getCourseInfo(userCourseDict[uid][i]) for i in range(start, min(len(userCourseDict[uid]), start + 20))],
                         'total': len(userCourseDict[uid])})


@require_http_methods(['GET'])
def checkEnrolled(request):
    uid = int(request.GET['uid'])
    courseid = int(request.GET['courseid'])
    enrolled = False
    if len(Enrollment.objects.filter(uid=uid, courseid=courseid)):
        enrolled = True
    return JsonResponse({'respMsg': enrolled, 'respCode': '200'})


@csrf_exempt
@require_http_methods(['POST'])
def enroll(request):
    en = Enrollment(id=Enrollment.objects.latest('id').id + 1, uid=request.POST['uid'], courseid=request.POST['courseid'])
    en.save()
    return JsonResponse({'respMsg': 'succeed', 'respCode': '200'})


@csrf_exempt
@require_http_methods(['POST'])
def leaveComment(request):
    comment = Comment(uid=int(request.POST['uid']), courseid=int(request.POST['courseid']), content=request.POST['content'], timeleft=datetime.datetime.now(), deleted=0)
    comment.save()
    return JsonResponse({'comment': setUserInfoInComment(comment.to_dict())})


@csrf_exempt
@require_http_methods(['GET'])
def showComments(request):
    comments = [setUserInfoInComment(c.to_dict()) for c in Comment.objects.filter(courseid=int(request.GET['courseid']), deleted=0)]
    return JsonResponse({'comments': comments})


@require_http_methods(['GET'])
def alarmComment(request):
    c = Comment.objects.get(id=int(request.GET['id']))
    c.deleted = 1
    c.save()
    return JsonResponse({'respMsg': 'succeed', 'respCode': '200'})


@require_http_methods(['GET'])
def deleteComment(request):
    c = Comment.objects.get(id=int(request.GET['id']))
    c.deleted = 2
    c.save()
    return JsonResponse({'respMsg': 'succeed', 'respCode': '200'})


@require_http_methods(['GET'])
def obtainAlarmedComments(request):
    comments = [setUserInfoInComment(comment.to_dict()) for comment in Comment.objects.filter(deleted=1)]
    return JsonResponse({'comments': comments})


@require_http_methods(['GET'])
def getRelativeCourses(request):
    courseList = []
    courseId = int(request.GET['cid'])
    result = itemCF.recommendBasedOnItem(courseId).keys()
    for i in result:
        courseList.append(getCourseInfo(i))
    return JsonResponse({'courseList': courseList})
