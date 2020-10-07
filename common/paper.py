from django.http import JsonResponse
import json
from common import models
from django.db.models import Q,F
from django.core.paginator import Paginator, EmptyPage#用于分页


def paper(request):
        if request.method == 'GET':
            request.params = request.GET
        elif request.method in ['POST', 'PUT', 'DELETE']:
            request.params = json.loads(request.body)
        action = request.params['action']

        if action == 'listbypage':
            return listbypage(request)
        elif action == 'getone':
            return getone(request)
        if 'usertype' in request.session:
            if action == 'addone':
                return addone(request)
            elif action == 'modifyone':
                return modifyone(request)
            elif action == 'listbypage_allstate':
                return listbypage_allstate(request)
            elif action == 'deleteone':
                return deleteone(request)
            elif action == 'banone':
                return banone(request)
            elif action == 'publishone':
                return publishone(request)
            elif action == 'listminebypage':
                return listminebypage(request)
            elif action == 'holdone':
                return holdone(request)
        else:
            return JsonResponse({'ret':1,'msg':'未登录'})

def listbypage(request):
    pagesize = request.params['pagesize']
    pagenum = request.params['pagenum']
    keywords = request.params['keywords']

    if 'withoutcontent' in request.params:
        data = models.paper.objects.values('id','pubdate', 'author', 'author__realname', 'title', 'content','thumbupcount',
                                            'status').filter(status=1).order_by('id')
    else:data = models.paper.objects.values('id','pubdate','author','author__realname','title','thumbupcount',
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
    if request.session['usertype'] == 1:
        pagesize = request.params['pagesize']
        pagenum = request.params['pagenum']
        keywords = request.params['keywords']

        data = models.paper.objects.values('id','pubdate', 'author', 'author__realname', 'title', 'content','status','thumbupcount').order_by('id')
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
    else:
        return JsonResponse({'ret': 1, 'msg': '不是管理员账号'})

def getone(request):
    id = request.params['id']
    getone = models.paper.objects.filter(id = id).values('id','pubdate', 'author',
                                                          'author__realname', 'title', 'content','status')
    one = getone[0]
    return JsonResponse({'ret':0,'rec':one})

def addone(request):
    data = request.params['data']
    one = models.paper.objects.create(title=data['title'],content=data['content'],author_id=request.session['id'])
    return JsonResponse({'ret':0,'id':one.id})


def modifyone(request):

    id = request.params['id']
    newdata = request.params['newdata']
    modifyone = models.paper.objects.get(id = id)
    if modifyone.author_id == request.session['id']:
        if 'title' in newdata:
            modifyone.title = newdata['title']
        if 'content' in newdata:
            modifyone.content = newdata['content']
        modifyone.save()
        return JsonResponse({'ret':0})
    else:
        return ({'ret':1,'msg':'不是作者本人,无法进行修改'})


def deleteone(request):
    id = request.params['id']
    delone = models.paper.objects.get(id = id)
    if request.session['usertype'] == 1 or delone.author_id == request.session['id']:
        delone.delete()
        return JsonResponse({'ret':0})
    else:
        return ({'ret':1,'msg':'只有管理员或本文作者才可删除本文章'})


def banone(request):
    if request.session['usertype'] == 1:
        id = request.params['id']
        banone = models.paper.objects.get(id=id)
        banone.status = 3
        banone.save()
        return JsonResponse({'ret': 0,'status':banone.status})
    else:
        return JsonResponse({'ret': 1, 'msg': '不是管理员账号'})
def publishone(request):
    if request.session['usertype'] == 1:
        id = request.params['id']
        publishone = models.paper.objects.get(id=id)
        publishone.status = 1
        publishone.save()
        return JsonResponse({'ret': 0, 'status': publishone.status})
    else:
        return JsonResponse({'ret': 1, 'msg': '不是管理员账号'})

def listminebypage(request):
    if request.session['usertype'] in [2000,3000]:
        pagesize = request.params['pagesize']
        pagenum = request.params['pagenum']
        keywords = request.params['keywords']
        author_id = request.session['id']
        data = models.paper.objects.filter(author=author_id).values('id','pubdate', 'author', 'author__realname', 'title', 'content','status','thumbupcount').order_by('id')
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
    else:
        return JsonResponse({'ret': 1, 'msg': '只有学生/教师才可以查看'})

def holdone(request):
    id = request.params['id']
    user_id = request.session['id']
    one = models.paper.objects.get(id = id)
    author_id = one.author_id
    if user_id == author_id:
        one.status=2
        one.save()
        return JsonResponse({'ret':0,'status':one.status})
    else:
        return JsonResponse({'ret':1,'msg':'不是作者本人'})