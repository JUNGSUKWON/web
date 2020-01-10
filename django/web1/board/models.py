from django.db import models

# Create your models here.

class Table1(models.Model): # 상속 받기 
    objects = models.Manager() # vs code 오류 제거용

    # 자동 입력, 기본키 
    no = models.AutoField(primary_key = True) 
    # 제목은 문자타입, 길이 200
    title = models.CharField(max_length = 200 ) 
    # 내용은 길이가 길기 때문에 text로 
    content = models.TextField() 
    writer = models.CharField(max_length = 50) 
    hit = models.IntegerField()
    # 바이너리 필드 
    img = models.BinaryField(null = True) 
    # auto_now_add는 자동으로 넣는다는 의미 
    regdate = models.DateField(auto_now_add = True) 


class Table2(models.Model):
    objects = models.Manager() # vs code 오류 제거용

    no = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    kor = models.IntegerField()
    eng = models.IntegerField()
    math = models.IntegerField()
    regdate = models.DateTimeField(auto_now_add=True)




