from django.http import JsonResponse
import json
from common import models
from django.db.models import Q,F
from django.core.paginator import Paginator, EmptyPage#用于分页


def news(request):

        if request.method == 'GET':
            request.params = request.GET
        elif request.method in ['POST', 'PUT', 'DELETE']:
            request.params = json.loads(request.body)
        action = request.params['action']

        if action == 'listbypage':
            return listbypage(request)
        elif action == 'getone':
            return getone(request)
        elif'usertype' in request.session:
            if request.session['usertype'] == 1:
                if action=='listbypage_allstate':
                    return listbypage_allstate(request)
                elif action == 'addone':
                    return addone(request)
                elif action == 'modifyone':
                    return modifyone(request)
                elif action == 'deleteone':
                    return deleteone(request)
                elif action == 'banone':
                    return banone(request)
                elif action == 'publishone':
                    return publishone(request)
            else:
                return JsonResponse({'ret':1,'msg':'不是管理员账号'})
        else:
            return JsonResponse({'ret':1,'msg':'未登录'})

def listbypage(request):
    pagesize = request.params['pagesize']
    pagenum = request.params['pagenum']
    keywords = request.params['keywords']

    if 'withoutcontent' in request.params:
        data = models.notice.objects.values('id','pubdate', 'author', 'author__realname', 'title', 'content',
                                            'status').filter(status=1).order_by('id')
    else:data = models.notice.objects.values('id','pubdate','author','author__realname','title',
                                             'status').filter(status=1).order_by('id')
    if keywords:
        query = Q()
        conditions = [Q(title__contains=i) for i in keywords.split(' ')]
        for i in conditions:
            query &= i
        data = data.filter(query)
    else:
        keywords = ''
    try:
        data = Paginator(data,pagesize)
        page = data.page(pagenum)
        page_list = list(page)
        return JsonResponse({'ret':0,'items':page_list,"total": data.count,"keywords":keywords})

    except EmptyPage:
        return JsonResponse({'ret': 0, 'items': [], 'total': 0,"keywords":keywords})

def listbypage_allstate(request):
    pagesize = request.params['pagesize']
    pagenum = request.params['pagenum']
    keywords = request.params['keywords']

    data = models.notice.objects.values('id','pubdate', 'author', 'author__realname', 'title', 'content','status').order_by('id')
    if keywords:
        query = Q()
        conditions = [Q(title__contains=i) for i in keywords.split(' ')]
        for i in conditions:
            query &= i
        data = data.filter(query)
    else:
        keywords = ''
    try:
        data = Paginator(data, pagesize)
        page = data.page(pagenum)
        page_list = list(page)
        return JsonResponse({'ret': 0, 'items': page_list, "total": data.count, "keywords": keywords})

    except EmptyPage:
        return JsonResponse({'ret': 0, 'items': [], 'total': 0, "keywords": keywords})

def getone(request):
    id = request.params['id']
    getone = models.notice.objects.filter(id = id).values('id','pubdate', 'author',
                                                          'author__realname', 'title', 'content','status')
    one = getone[0]
    return JsonResponse({'ret':0,'rec':one})

def addone(request):
    data = request.params['data']
    one = models.notice.objects.create(title=data['title'],content=data['content'],author_id=request.session['id'])
    return JsonResponse({'ret':0,'id':one.id})


def modifyone(request):
    id = request.params['id']
    newdata = request.params['newdata']
    modifyone = models.notice.objects.get(id = id)
    if 'title' in newdata:
        modifyone.title = newdata['title']
    if 'content' in newdata:
        modifyone.content = newdata['content']
    modifyone.save()
    return JsonResponse({'ret':0})


def deleteone(request):
    id = request.params['id']
    delone = models.notice.objects.get(id = id)
    delone.delete()
    return JsonResponse({'ret':0})


def banone(request):
    id = request.params['id']
    banone = models.notice.objects.get(id=id)
    banone.status = 3
    banone.save()
    return JsonResponse({'ret': 0,'status':banone.status})
def publishone(request):
    id = request.params['id']
    publishone = models.notice.objects.get(id=id)
    publishone.status = 1
    publishone.save()
    return JsonResponse({'ret': 0, 'status': publishone.status})