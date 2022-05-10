# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: { 课程相关的业务 }
# @Date: 2022/3/4 9:48 下午
import pytz
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rec.TagBasedRatingSort.clusterBasedSort import recommendCourseList, recommendType, getClusterIntention
from .verify import *
import datetime

from .util import *


# 获取经典推荐
@require_http_methods(["GET"])
def getRecommendCourses(request):
    response = {}
    courseList = []
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
userCourseList = {-1: recommendCourseList(-1)}  # 把请求过的用户的结果保存下来, 但这种用变量存储的方式不仅危险，而且不易于更新，基本上相当于定死了
userIntentionList = {-1: []}
allTypeList = dict()


@require_http_methods(['GET'])
def getAllRecommends(request, uid, start, t):
    verify_recommends_params(int(uid), int(start), int(t))
    uid = int(uid) - 1
    courseList = []
    if int(t) == 0:
        intentionList = [i.tid for i in Intention.objects.filter(uid=int(uid))]
        intentionList.sort()
        if userIntentionList.get(uid, 0) == 0 or intentionList != userIntentionList.get(uid, 0):
            userIntentionList[uid] = intentionList
            userCourseList[uid] = recommendCourseList(int(uid))
        for i in range(int(start), min(int(start) + 20, len(userCourseList[uid]))):
            courseList.append(getCourseInfo(userCourseList[uid][i][0]))
        return JsonResponse({'courseList': courseList, 'total': len(userCourseList[uid])})
    else:
        if allTypeList.get(int(t), 0) == 0:
            allTypeList[t] = recommendType(int(t))
        for i in range(int(start), min(int(start) + 20, len(allTypeList[t]))):
            courseList.append(getCourseInfo(allTypeList[t][i]))
        return JsonResponse({'courseList': courseList, 'total': len(allTypeList[t])})


@csrf_exempt
@require_http_methods(['POST'])
def createClass(request):
    request = verify_class_params(request)
    c = Course(id=Course.objects.latest('id').id + 1, type=int(request.POST['type']), name=request.POST['name'],
               abstract=request.POST.get('abstract', None), tid=int(request.POST['tid']),
               time=datetime.datetime.now(), link=request.POST['link'] if request.POST['link'] != '' else None)
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
    return JsonResponse({'courseList': [getCourseInfo(teacherCourseDict[tid][i]) for i in
                                        range(start, min(len(teacherCourseDict[tid]), start + 20))],
                         'total': len(teacherCourseDict[tid])})


userCourseDict = dict()


@require_http_methods(['GET'])
def getUserRegisterCourse(request):
    uid = int(request.GET['uid'])
    start = int(request.GET['start'])
    if userCourseDict.get(uid, 0) == 0:
        userCourseDict[uid] = [c.courseid for c in Enrollment.objects.filter(uid=uid)]
    return JsonResponse({'courseList': [getCourseInfo(userCourseDict[uid][i]) for i in
                                        range(start, min(len(userCourseDict[uid]), start + 20))],
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
    en = Enrollment(id=Enrollment.objects.latest('id').id + 1, uid=request.POST['uid'],
                    courseid=request.POST['courseid'])
    en.save()
    return JsonResponse({'respMsg': 'succeed', 'respCode': '200'})


@csrf_exempt
@require_http_methods(['POST'])
def leaveComment(request):
    comment = Comment(uid=int(request.POST['uid']), courseid=int(request.POST['courseid']),
                      content=request.POST['content'], timeleft=datetime.datetime.now(), deleted=0)
    comment.save()
    return JsonResponse({'comment': setUserInfoInComment(comment.to_dict())})


@csrf_exempt
@require_http_methods(['GET'])
def showComments(request):
    comments = [setUserInfoInComment(c.to_dict()) for c in
                Comment.objects.filter(courseid=int(request.GET['courseid']), deleted=0)]
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


@require_http_methods(['GET'])
def searchCourses(request):
    keyWord = list(request.GET['keyWord'])

    def score(courseId):
        c = Course.objects.get(id=courseId)
        r = 0
        for s in keyWord:
            if s in c.name:
                r += 1
        return r

    courseList = []
    for k in keyWord:
        courseList.extend([c.id for c in Course.objects.filter(name__icontains=k)])
    courseList = list(set(courseList))
    t = len(courseList)
    courseList.sort(key=score, reverse=True)
    courseList = courseList[(int(request.GET['start']) - 1) * 20: min(t, int(request.GET['start']) * 20)]
    courseList = [getCourseInfo(c) for c in courseList]
    return JsonResponse({'courseList': courseList, 'total': t})


@require_http_methods(['GET'])
def newlyRecommend(request):
    newlyDate = datetime.datetime(2022, 3, 11, 0, 0, 0)
    newlyDate = newlyDate.replace(tzinfo=pytz.timezone('UTC'))
    courseList = [c.id for c in Course.objects.filter() if c.time.__gt__(newlyDate)]
    courseList.sort(key=lambda x: len(Enrollment.objects.filter(courseid=x)), reverse=True)
    courseList = [getCourseInfo(c) for c in courseList]
    return JsonResponse({'courseList': courseList[:5]})


@require_http_methods(['GET'])
def intention(request):
    cur_uid = int(request.GET['uid'])
    intentionList = getClusterIntention(cur_uid)
    intentionSum = sum(intentionList)
    intentionList = [100 * j / intentionSum for j in intentionList]
    intentionNameList = [CourseType.objects.get(id=i + 1).name for i in range(len(intentionList))]
    return JsonResponse({'intention': intentionList, 'typeName': intentionNameList})
