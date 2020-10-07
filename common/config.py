import json
from django.http import JsonResponse
from common import models
from django.db.models import Q

def config(request):
    if request.method == 'GET':
        request.params = request.GET
    elif request.method in ['POST','PUT','DELETE']:
        request.params = json.loads(request.body)

    action = request.params['action']
    if action == 'set':
        return sethomepage(request)
    elif action == 'gethomepagebyconfig':
        return gethomepage(request)
    elif action == 'get':
        return forget(request)

def sethomepage(request):
    if request.session['usertype'] == 1:
        value = (request.params['value'])
        new_page = models.homepage.objects.create(value=value)
        return JsonResponse({'ret':0})
    else:
        return JsonResponse({'ret':1,'msg':'不是管理员'})
def gethomepage(request):
    
        new_set = models.homepage.objects.last()
        last_value = new_set.value
        notice = eval(last_value)['notice']
        news = eval(last_value)['news']
        paper = eval(last_value)['paper']
        if notice:
            notice_data =models.notice.objects.values('id','pubdate', 'author',
                                                          'author__realname', 'title', 'content','status')
            query=Q()
            conditions = [Q(id = i) for i in notice]
            for i in conditions:
                query |= i
            notice_data = notice_data.filter(query)
            notice = list(notice_data)
        if news:
            news_data = models.news.objects.values('id', 'pubdate', 'author',
                                                       'author__realname', 'title', 'content', 'status')
            query = Q()
            conditions = [Q(id=i) for i in news]
            for i in conditions:
                query |= i
            news_data = news_data.filter(query)
            news = list(news_data)
        if paper:
            paper_data = models.paper.objects.values('id', 'pubdate', 'author',
                                                       'author__realname', 'title', 'content', 'status')
            query = Q()
            conditions = [Q(id=i) for i in paper]
            for i in conditions:
                query |= i
            paper_data = paper_data.filter(query)
            paper = list(paper_data)
        homepage_dict = {'notice':notice,'news':news,'paper':paper}
        return JsonResponse({'ret':0,'info':homepage_dict})

def forget(request):
    one = models.homepage.objects.last()
    value = one.value
    return JsonResponse({
        'ret':0,
        'value':value
    })