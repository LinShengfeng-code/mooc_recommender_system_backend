# -*- coding: utf-8 -*-
# @Author: Lin Shengfeng
# @Desc: { 转换注册数据到数据库 }
# @Date: 2022/3/10 9:39 下午
import csv
from web.models import *


def readEnrollment():
    enrollment_list = []
    # 因为存在中文，所以以GBK编码形式读取
    csv_reader = csv.reader(open('data.csv', encoding='GBK'))
    for row in csv_reader:
        enrollment_list.append(row)
    return enrollment_list[1:]


if __name__ == '__main__':
    enrollments = readEnrollment()
    for en in enrollments:
        enrollment = Enrollment(uid=int(en[0]), courseid=int(en[2]))
        enrollment.save()