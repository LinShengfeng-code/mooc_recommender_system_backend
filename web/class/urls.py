# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: {}
# @Date: 2022/3/4 9:48 下午
from django.conf.urls import url

from .views import *

urlpatterns = [
    url("get_recommend", getRecommendCourses),
    url(r'get_single_course/(\d+)', getSingleCourseInfo),
    url('get_all_types', getAllTypes),
    url(r'get_all_recommends/(\d+)/(\d+)/(\d+)', getAllRecommends),
    url('create', createClass),
    url('valid_name', validClassName),
    url('get_teacher_course', getTeacherCourse),
    url('get_user_register_course', getUserRegisterCourse),
    url('check_enrolled', checkEnrolled),
    url('enroll', enroll),
    url('leave_comment', leaveComment),
    url('show_comments', showComments),
    url('alarm_comment', alarmComment),
    url('delete_comment', deleteComment),
    url('obtain_alarmed_comments', obtainAlarmedComments),
    url('get_relative_courses', getRelativeCourses),
    url('search_courses', searchCourses),
    url('newly_recommend', newlyRecommend)
]