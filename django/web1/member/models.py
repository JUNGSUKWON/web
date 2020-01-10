from django.db import models

# Create your models here.

class Table2(models.Model):
    objects = models.Manager()

    no = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    kor = models.IntegerField()
    eng = models.IntegerField()
    math = models.IntegerField()
    classroom = models.CharField(max_length=3)
    regdate = models.DateTimeField(auto_now_add=True)

    ## 실습과제
    #1. 회원을 20명 추가하시오

    #urls.py
    # exam_insert
    # exam_update
    # exam_delete
    # exam_select
