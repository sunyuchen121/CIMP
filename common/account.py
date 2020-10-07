from common import models
import json
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage#用于分页
from django.db.models import Q
from django.db.models import F #用于重命名

def list_user(request):
    if request.session['usertype'] == 1:
        if request.method == 'GET':
            request.params = request.GET
        elif request.method in ['POST','PUT','DELETE']:
            request.params = json.loads(request.body)
        action = request.params['action']

        if action == 'listbypage':
            return listbypage(request)
        elif action == 'addone':
            return add(request)
        elif action == 'modifyone':
            return modify(request)
        elif action == 'deleteone':
            return delete(request)
    else:
        return JsonResponse({'ret':1,'msg':'不是管理员,无法进行账号管理'})

def listbypage(request):
    try:
        #一页包含多少条记录
        pagesize = request.params['pagesize']
        #第几页
        pagenum = request.params['pagenum']
        #关键字
        keywords = request.params['keywords']    #order_by('id') 按照ID升序排列，为了下边的分页有数据的排序  也可以按别的方式排列如'name'
        data = models.User.objects.values('id','username','realname','studentno','desc','usertype').order_by('-id')
        if keywords:                             #order_by('-id')按id降序排列
            query = Q()
            conditions = [Q(username__contains=i) for i in keywords.split(' ')]
            for i in conditions:
                query &= i
            data = data.filter(query)
        else:
            keywords = ''

        #将所有记录返回一个分页对象
        data = Paginator(data,pagesize)
        #page是分页对象中第pagenum页的所有记录
        page = data.page(pagenum)
        data_list = list(page)
        return JsonResponse({'ret':0,'items':data_list,'total':data.count,'keywords':keywords}) #.count表示包含的所有记录数 如果一页5条，第三页，那total就是15
    except EmptyPage:
        return JsonResponse({'ret': 0, 'items': [], 'total': 0})


def add(request):
    data = request.params['data']
    addone = models.User.objects.create(realname = data['realname'],username = data['username'],password = make_password(data['password']),studentno= data['studentno'],desc =data['desc'],usertype = data['usertype'])

    return JsonResponse({'ret':0,'id':addone.id})


def modify(request):
    id = request.params['id']
    try:
        modifyone = models.User.objects.get(id = id)
    except models.User.DoesNotExist:
        return ({'ret':1,'msg':'需要修改的账号id不存在'})
    newdata = request.params['newdata']

    if 'realname' in newdata:
        modifyone.realname = newdata['realname']
    if 'username' in newdata:
        modifyone.username = newdata['username']
    if 'studentno' in newdata:
        modifyone.studentno = newdata['studentno']
    if 'password' in newdata:
        modifyone.password = newdata['password']
    if 'desc' in newdata:
        modifyone.desc = newdata['desc']

    modifyone.save()
    return JsonResponse({'ret':0,})

def delete(request):
    id = request.params['id']
    deleteone = models.User.objects.get(id = id)
    deleteone.delete()
    return JsonResponse({"ret": 0})