import json
from django.http import JsonResponse
from common import models
from django.db import transaction #用于事务
from django.contrib.auth.hashers import make_password


def myconfig(request):
    if request.method == 'GET':
        request.params = request.GET
    elif request.method in ['POST', 'PUT', 'DELETE']:
        request.params = json.loads(request.body)
    if request.session['usertype'] in [2000,3000]:
        action = request.params['action']
        if action == 'setmyprofile':
            return setmyprofile(request)
        elif action == 'getmyprofile':
            return getmyprofile(request)
        elif action == 'thumbuporcancel':
            return thumbuporcancel(request)
        elif action == 'listteachers':
            return listteachers(request)

def getmyprofile(request):
    id = request.session['id']
    getone = models.User.objects.get(id=id)
    if request.session['usertype'] == 2000:
        if getone.teacherid:
            teacher = models.User.objects.get(id = getone.teacherid)
            data = {
                'userid':getone.id,
                'usertype':getone.usertype,
                'realname':getone.realname,
                'username':getone.username,
                'teacher': {
                    'id': getone.teacherid,
                    'realname': teacher.realname
                }
            }
        else:
            data = {
                'userid': getone.id,
                'usertype': getone.usertype,
                'realname': getone.realname,
                'username': getone.username,
                'teacher': {
                    'id': '',
                    'realname': ''
                }
            }
    if request.session['usertype'] == 3000:
        data = {
            'userid': getone.id,
            'usertype': getone.usertype,
            'realname': getone.realname,
            'username': getone.username,
            }
    return JsonResponse({'ret':0,'profile':data})


def setmyprofile(request):
    id = request.session['id']
    getone = models.User.objects.get(id=id)
    if 'teacherid' in request.params['newdata']:
        teacherid = request.params['newdata']['teacherid']
        getone.teacherid = teacherid
    if 'realname' in request.params['newdata']:
        realname = request.params['newdata']['realname']
        getone.realname = realname
    if 'password' in request.params['newdata']:
        password = request.params['newdata']['password']
        getone.password = make_password(password)
    getone.save()
    return JsonResponse({'ret': 0})


def listteachers(request):
    teachers = models.User.objects.filter(usertype=3000).values('id','realname')
    teachers = list(teachers)
    all_tea = len(teachers)
    return JsonResponse({'ret':0,'items':teachers,'total':all_tea,'keywords':''})


def thumbuporcancel(request):
        id = request.params['paperid']
        one = models.thumbuporcancel.objects.filter(thumbuporcancel_paper_id=id,user_id=request.session['id'])
        if one:
            with transaction.atomic():
                one = one[0]
                one.delete()
                paper_zan = models.paper.objects.get(id = id)
                paper_zan.thumbupcount -= 1
                paper_zan.save()
        else:
            with transaction.atomic():
                add = models.thumbuporcancel.objects.create(thumbuporcancel_paper_id = id,user_id=request.session['id'])
                paper_zan = models.paper.objects.get(id=id)
                paper_zan.thumbupcount += 1
                paper_zan.save()

        return JsonResponse({
      "ret": 0,
      "thumbupcount": models.paper.objects.get(id = id).thumbupcount
    })