from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
class User(AbstractUser):
    usertype = models.PositiveIntegerField(db_index=True) #PositiveIntegerField正整数或0(非负整数）
    realname = models.CharField(max_length=10)
    studentno = models.CharField(max_length=20,null=True,blank=True)
    desc = models.CharField(max_length=200,null=True,blank=True)
    teacherid = models.IntegerField(null=True,blank=True)
    REQUIRED_FIELDS = ['usertype', 'realname']
    class Meta: #class Meta做为嵌套类，主要目的是给上级类添加一些功能，或者指定一些标准
        db_table = 'cimp_user' #指定表名为cimp_user 弃用的用户表为auth


class notice(models.Model):
    pubdate =models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    title =models.CharField(max_length=100)
    content = models.CharField(max_length=1000)
    status = models.IntegerField(default=1)

class news(models.Model):
    pubdate =models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    title =models.CharField(max_length=100)
    content = models.CharField(max_length=1000)
    status = models.IntegerField(default=1)

class paper(models.Model):
    pubdate =models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    title =models.CharField(max_length=100)
    content = models.CharField(max_length=1000)
    status = models.IntegerField(default=1)
    thumbupcount = models.IntegerField(default=0)

class homepage(models.Model):
    value = models.CharField(max_length=100)

class thumbuporcancel(models.Model):
    thumbuporcancel_paper = models.ForeignKey(paper,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

class workf(models.Model):
    creator = models.ForeignKey(User,on_delete=models.CASCADE,related_name='work')
    createdate = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    currentstate = models.CharField(max_length=50)
    teacher = models.CharField(max_length=50,null=True,blank=True)



class steps(models.Model):
    actionname = models.CharField(max_length=200)
    creattime = models.DateTimeField(auto_now_add=True)
    nextstate = models.CharField(max_length=100)
    operator = models.ForeignKey(User,on_delete=models.CASCADE)
    work = models.ForeignKey(workf,on_delete=models.CASCADE,related_name='work_step')
    key = models.CharField(max_length=100,default='')

class submitdata(models.Model):
    name = models.CharField(max_length=200)
    data = models.TextField(default='')
    type = models.CharField(max_length=100)
    step = models.ForeignKey(steps, on_delete=models.PROTECT,default='')



