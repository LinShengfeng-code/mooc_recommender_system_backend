from django.db import models
from django.db.models import Model, ForeignKey
from mooc_back_end.settings import MEDIA_ROOT
"""
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'web.settings'
"""


# Create your models here.
class User(Model):
    uid = models.IntegerField(verbose_name='uid', primary_key=True)  # 用户编号
    mail = models.CharField(max_length=255, verbose_name='mail', unique=True)  # 邮箱
    password = models.CharField(max_length=255, verbose_name='password')  # 用户密码
    nick = models.CharField(max_length=255, verbose_name='nick', unique=True)  # 用户昵称
    type = models.IntegerField(verbose_name='type')  # 用户类型, 0: 管理员, 1: 教师, 2: 学生
    avatar = models.ImageField(upload_to='web/img/avatar', blank=True, null=True)

    def __unicode__(self):
        return self.uid

    def __str__(self):
        return self.uid

    def to_dict(self):
        return {'uid': self.uid, 'mail': self.mail, 'nick': self.nick, 'type': self.type, 'avatar': str(self.avatar)}

    class Meta:
        db_table = 'web_user'


class Student(Model):
    uid = models.IntegerField(verbose_name='uid', primary_key=True)
    sid = models.IntegerField(verbose_name='sid')
    cid = models.IntegerField(verbose_name='cid')
    intime = models.IntegerField(verbose_name='intime')
    degree = models.IntegerField(verbose_name='degree')

    class Meta:
        db_table = 'web_student'


class Teacher(Model):
    uid = models.IntegerField(verbose_name='uid', primary_key=True)
    sid = models.IntegerField(verbose_name='sid')
    cid = models.IntegerField(verbose_name='cid')

    class Meta:
        db_table = 'web_teacher'


class School(Model):
    sid = models.IntegerField(verbose_name='sid', primary_key=True)  # 学校代码
    sname = models.CharField(max_length=255, verbose_name='sname')  # 学校名称

    def __unicode__(self):
        return self.sid

    def __str__(self):
        return "{0} {1}".format(str(self.sid), self.sname)

    class Meta:
        db_table = 'web_school'


class College(Model):
    sid = models.IntegerField(verbose_name='sid')  # 学院的校编号是外键， 关联了学校的编号
    cid = models.IntegerField(verbose_name='cid', primary_key=True)  # 学院在该学校的编号
    cname = models.CharField(max_length=255, verbose_name='cname')  # 学院名称

    class Meta:
        unique_together = ("sid", "cid")
        db_table = 'web_college'


class Course(Model):
    id = models.IntegerField(verbose_name='id', primary_key=True)
    name = models.CharField(verbose_name='name', max_length=255)
    abstract = models.CharField(verbose_name='abstract', max_length=255)
    tid = models.IntegerField(verbose_name='tid')
    time = models.DateTimeField(verbose_name='time')
    type = models.IntegerField(verbose_name='type')
    link = models.CharField(max_length=255, verbose_name='link', null=True)
    img = models.ImageField(upload_to='web/img/class', blank=True, null=True)

    class Meta:
        db_table = 'web_course'


class Enrollment(Model):
    id = models.IntegerField(verbose_name='id', primary_key=True)
    uid = models.IntegerField(verbose_name='uid')
    courseid = models.IntegerField(verbose_name='courseid')

    class Meta:
        db_table = 'web_enrollment'


class CourseType(Model):
    id = models.IntegerField(verbose_name='id', primary_key=True)
    name = models.CharField(max_length=255, verbose_name='name')

    class Meta:
        db_table = 'web_course_type'


class Comment(Model):
    id = models.AutoField(verbose_name='id', primary_key=True)
    uid = models.IntegerField(verbose_name='uid')
    courseid = models.IntegerField(verbose_name='courseid')
    content = models.CharField(max_length=255)
    timeleft = models.DateTimeField(verbose_name='timeleft')
    deleted = models.IntegerField(verbose_name='deleted')

    def to_dict(self):
        return {'id': self.id, 'uid': self.uid, 'courseid': self.courseid, 'content': self.content, 'timeleft': self.timeleft}

    class Meta:
        db_table = 'web_comment'