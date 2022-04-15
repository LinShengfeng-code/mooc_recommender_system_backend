# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: { 课程数据转到数据库 }
# @Date: 2022/3/10 9:40 下午
import csv
import datetime

from web.models import *

"""
def readCourses():
    course_list = []
    # 因为存在中文，所以以GBK编码形式读取
    csv_reader = csv.reader(open('link_copy.csv', encoding='GBK'))
    for row in csv_reader:
        course_list.append(row)
    return course_list[1:]
"""


def readLinkedCourses():
    course_list = []
    # 因为存在中文，所以以GBK编码形式读取
    csv_reader = csv.reader(open('link.csv', encoding='GBK'))
    for row in csv_reader:
        course_list.append(row)
    return course_list[1:]


if __name__ == '__main__':
    course_list = readLinkedCourses()
    for c in course_list:
        if c[2] != '':
            course = Course.objects.get(id=c[0])
            course.link = c[2]
            course.save()
    """
    for c in course_list:
        course = Course(id=int(c[0]), name=c[2], type=int(c[1]), tid=20, time=datetime.datetime.now())
        course.save()
    """
