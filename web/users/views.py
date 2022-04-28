import json

from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from mooc_back_end.settings import MEDIA_ROOT
from utils.token.tokenUtils import *
from .verify import *
import hashlib
import time


# 查询所有学校
@require_http_methods(["GET"])
def show_schools(request):
    response = {}
    try:
        schools = School.objects.filter()
        response['list'] = json.loads(serializers.serialize("json", schools))
        response['respMsg'] = 'success'
        response['respCode'] = '200'
    except Exception as e:
        print(e)
        response['respMsg'] = 'Failed to load all schools.'
        response['respCode'] = '404'
    return JsonResponse(response)


# 查询某学校下的所有学院
@require_http_methods(["GET"])
def show_colleges(request):
    response = {}
    try:
        re_sid = int(request.GET['sid'])
        colleges = College.objects.filter(sid=re_sid)
        response['list'] = json.loads(serializers.serialize("json", colleges))
        response['respMsg'] = 'success'
        response['respCode'] = '200'
    except Exception as e:
        print(e)
        response['respMsg'] = 'Failed to load correspond colleges.'
        response['respCode'] = '404'
    return JsonResponse(response)


# 邮箱查重
@require_http_methods(["GET"])
def mail_repeat(request):
    response = {}
    try:
        re_mail = request.GET['mail']
        mail = User.objects.filter(mail=re_mail)
        if len(mail):
            response['respMsg'] = False  # 邮箱已被注册
        else:
            response['respMsg'] = True  # 邮箱可用
        response['respCode'] = '200'
    except Exception as e:
        response['respMsg'] = e
        response['respCode'] = '404'
    return JsonResponse(response)


# 昵称查重
@require_http_methods(["GET"])
def nick_repeat(request):
    response = {}
    try:
        re_nick = request.GET['nick']
        nick = User.objects.filter(nick=re_nick)
        if len(nick):
            response['respMsg'] = False  # 昵称已被注册
        else:
            response['respMsg'] = True  # 昵称可用
        response['respCode'] = '200'
    except Exception as e:
        response['respMsg'] = e
        response['respCode'] = '404'
    return JsonResponse(response)


# 插入新用户(学生/教师)
@csrf_exempt
@require_http_methods(['POST'])
def add_new_user(request):
    verify_register_params(request)
    response = {}
    register_data = json.loads(request.body.decode('utf-8'))
    # 先将用户导入 web_user 表
    new_user = User(mail=register_data['mail'], password=register_data['pwd'], nick=register_data['nick'], type=int(register_data['type']), avatar=None)
    new_user.save()
    # 再根据type对用户进行分流，学生导入 web_student 表, 教师导入 web_teacher 表
    # sid, cid 不论教师学生都需要
    u_sid, u_cid = int(register_data['sid']), int(register_data['cid'])
    u_uid = User.objects.get(mail=register_data['mail']).uid
    # type 1 教师, 2 学生, 0 管理员(直接导入数据表)
    if int(register_data['type']) == 1:
        new_teacher = Teacher(uid=u_uid, sid=u_sid, cid=u_cid)
        # 保存新教师用户
        new_teacher.save()
    elif int(register_data['type']) == 2:
        new_student = Student(uid=u_uid, sid=u_sid, cid=u_cid)
        u_intime, u_degree = -1, -1
        # intime 和 degree 不是必选项，所以要用默认值校验
        try:
            u_intime = int(register_data['intime'])
        except Exception as intime_error:
            print(intime_error)
        try:
            u_degree = int(register_data['degree'])
        except Exception as degree_error:
            print(degree_error)
        if u_intime > -1:
            new_student.intime = u_intime
        if u_degree > -1:
            new_student.degree = u_degree
        # 保存新学生用户
        new_student.save()
    response['token'] = create_token(new_user.nick)
    response['cur_user'] = json.dumps(User.objects.get(nick=new_user.nick).to_dict())
    return JsonResponse(response)


# 登录验证
@csrf_exempt
@require_http_methods(['POST'])
def log_in(request):
    verify_login_params(request)
    response = {}
    login_data = json.loads(request.body.decode('utf-8'))
    cur_usr = User.objects.get(mail=login_data['mail'])
    response['token'] = create_token(cur_usr.nick)
    response['cur_user'] = json.dumps(cur_usr.to_dict())
    return JsonResponse(response)


# 头像更新
@csrf_exempt
@require_http_methods(['POST'])
def update_avatar(request, cur_uid):
    avatar_img = verify_image(request)
    cur_user = User.objects.get(uid=cur_uid)
    if str(cur_user.avatar) != '':
        os.remove(MEDIA_ROOT + str(cur_user.avatar))
    avatar_img.name = hashlib.md5((str(cur_uid) + str(time.time())).encode('utf-8')).hexdigest() + '.jpg'
    cur_user.avatar = avatar_img
    cur_user.save()
    return JsonResponse({'avatar': str(cur_user.avatar)})


@require_http_methods(['GET'])
def hobbies(request):
    cur_uid = int(request.GET['uid'])
    hobbiesDict = dict()
    # 统计课程种类的学习次数
    for name in [CourseType.objects.get(id=Course.objects.get(id=en.courseid).type).name for en in Enrollment.objects.filter(uid=cur_uid)]:
        hobbiesDict[name] = hobbiesDict.get(name, 0) + 1
    return JsonResponse({'hobbies': hobbiesDict})


@require_http_methods(['GET'])
def schoolCollege(request):
    cur_uid = int(request.GET['uid'])
    try:
        if User.objects.get(uid=cur_uid).type == 1:
            t = Teacher.objects.get(uid=cur_uid)
            return JsonResponse({'school': School.objects.get(sid=t.sid).sname, 'college': College.objects.get(sid=t.sid, cid=t.cid).cname})
        elif User.objects.get(uid=cur_uid).type == 2:
            s = Student.objects.get(uid=cur_uid)
            return JsonResponse({'school': School.objects.get(sid=s.sid).sname, 'college': College.objects.get(sid=s.sid, cid=s.cid).cname})
    except Exception as e:
        print(e)
    return JsonResponse({'school': '暂无', 'college': '暂无'})


@require_http_methods(['GET'])
def interests(request):
    cur_uid = int(request.GET['uid'])
    interestList = []
    for interest in Intention.objects.filter(uid=cur_uid):
        interestList.append(CourseType.objects.get(id=interest.tid).name)
    return JsonResponse({'interestList': interestList})


@csrf_exempt
@require_http_methods(['POST'])
def modifyIntentions(request):
    intentionsData = json.loads(request.body.decode('utf-8'))
    cur_uid = intentionsData['uid']
    interestList = intentionsData['interestList']
    for interest in interestList:
        temp_tid = CourseType.objects.get(name=interest).id
        if len(Intention.objects.filter(uid=cur_uid, tid=temp_tid)) == 0:
            Intention(uid=cur_uid, tid=temp_tid).save()
    for interest in Intention.objects.filter(uid=cur_uid):
        if CourseType.objects.get(id=interest.tid).name not in interestList:
            interest.delete()
    return JsonResponse({'respMsg': 'success', 'respCode': '200'})