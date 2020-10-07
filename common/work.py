import json
from django.http import JsonResponse
from common import models
from django.core.paginator import Paginator, EmptyPage#用于分页
from django.db.models import Q,ObjectDoesNotExist,F
from django.db import transaction #用于事务


def work(request):
    if request.method == 'GET':
        request.params = request.GET
    elif request.method in ['PUT','DELETE','POST']:
        request.params = json.loads(request.body)

    action = request.params['action']
    if action=='listbypage':
        return listwork(request)
    elif action == 'getone':
        return getone(request)
    elif action == 'stepaction':
        return creat_step(request)
    elif action == 'getstepactiondata':
        return more(request)

def listwork(request):
    keywords = request.params['keywords']
    page = request.params['pagenum']
    pagesize = request.params['pagesize']
    if request.session['usertype'] == 2000:
        work = models.workf.objects.filter(creator_id = request.session['id']).values().order_by('id')
    elif request.session['usertype'] == 3000:
        work = models.workf.objects.filter(teacher=request.session['id']).values().order_by('id')
    if keywords:
        query = Q()
        conditions = [Q(contains = i) for i in keywords.split(' ')]
        for i in conditions:
            query &= i
        work = work.filter(query)
    else:
        keywords=''
    try:
        work = Paginator(work,pagesize)
        work_page = work.page(page)
        work_list = list(work_page)
        return JsonResponse({'ret':0,'items':work_list,'total':work.count,'keywords':keywords})
    except EmptyPage:
        return JsonResponse({'ret': 0, 'items': [], 'total': 0, "keywords": keywords})

def getone(request):
    try:
        id = request.session['id']
        work_id =request.params['wf_id']
        withwhatican = request.params['withwhatcanido']
        works = models.workf.objects.get(id = work_id)
        creator = models.User.objects.get(id = works.creator_id)
        step = models.steps.objects.annotate(actiondate=F('creattime')).filter(work_id = work_id).values('id','operator__realname','actiondate','actionname','nextstate')
        steps = list(step)
        submit = models.submitdata.objects.filter(step__work_id = work_id)
        work = {
                "id": works.id,
                "creatorname": creator.realname,
                "title": works.title,
                "currentstate": works.currentstate,
                "createdate": works.createdate,
                "steps":steps
                }
        now_state = work['currentstate']
        if withwhatican:
            if request.session['usertype'] == 2000:
                if now_state == '主题被驳回':
                    key='modify_topic'
                    name= '修改主题'
                    next= '主题已创建'
                    submitdata= [{'name': "毕业设计标题", 'type': "text", 'check_string_len': [2, 100]},
                    {'name': "主题描述", 'type': "richtext", 'check_string_len': [20,10000]}]
                    icando = [
                        {
                            'name': name,
                            'whocan': id,
                            'next': next,
                            'key': key,
                            'submitdata': submitdata,
                        }
                    ]
                elif now_state == '主题已通过':
                    action_name = '提交毕业设计'
                    next_state = '学生已提交毕业设计'
                    submit = [{'name':'毕业设计内容',"type": "richtext","check_string_len": [0,10000]}]
                    icando = [{
                        'name': action_name,
                        'key' : 'submit_design',
                        'next' : next_state,
                        'submitdata':submit,
                        'whocan':id
                    }]
                elif now_state in ['主题已创建','学生已提交毕业设计','已评分']:
                    icando = []

                return JsonResponse({'ret': 0, 'rec': work,'whaticando':icando})
            elif request.session['usertype'] == 3000:
                now_state = work['currentstate']
                if now_state == '主题已创建':
                    action_name = ['批准主题','驳回主题']
                    next = ['主题已通过','主题被驳回']
                    key = ['approve_topic','reject_topic']
                    submitdata = [
                        [{'name':'备注', "type": 'richtext',"check_string_len": [0,10000]}] ,
                        [{'name':'驳回原因', "type": 'textarea',"check_string_len": [0,10000]}]
                    ]
                    icando = [
                        {
                            'name': action_name[0],
                            'whocan': id,
                            'next': next[0],
                            'key': key[0],
                            'submitdata': submitdata[0],
                        },
                        {
                            'name': action_name[1],
                            'whocan': id,
                            'next': next[1],
                            'key': key[1],
                            'submitdata': submitdata[1],
                        }
                    ]

                elif now_state == '学生已提交毕业设计':
                    action_name = ['评分','打回重做']
                    next = ['已评分','主题已通过']
                    key = ['score_design','reject']
                    submitdata = [

                        [{'name': '评分细则', "type": 'richtext', "check_string_len": [0, 10000]}],
                        [{'name': '打回原因', "type": 'textarea', "check_string_len": [0, 10000]}]

                    ]
                    icando = [
                        {
                            'name': action_name[0],
                            'whocan': id,
                            'next': next[0],
                            'key': key[0],
                            'submitdata': submitdata[0],
                        },
                        {
                            'name': action_name[1],
                            'whocan': id,
                            'next': next[1],
                            'key': key[1],
                            'submitdata': submitdata[1],
                        }
                    ]
                elif now_state in ['主题被驳回','主题已通过','已评分','打回重做']:
                    icando = []
                return JsonResponse({'ret': 0, 'rec': work, 'whaticando': icando})
        else:
            return JsonResponse({'ret':0,'rec':work})
    except ObjectDoesNotExist:
        return JsonResponse({
  "ret": 0,
  "rec": {
    "id": -1,
    "creatorname": "",
    "title": "",
    "currentstate": "",
    "createdate": ""
  },
  "whaticando": [
    {
      "name": "创建主题",
      "submitdata": [
        {
          "name": "毕业设计标题",
          "type": "text",
          "check_string_len": [
            1,
            50
          ]
        },
        {
          "name": "主题描述",
          "type": "richtext",
          "check_string_len": [
            10,
            10000
          ]
        }
      ],
      "whocan": 1,
      "next": "主题已创建",
      "key": "create_topic"
    }
  ]
})


def creat_step(request):
    key = request.params['key']
    id = request.session['id']
    if key == 'create_topic':
        actionname = '创建主题'
        now_state = '主题已创建'
        with transaction.atomic():
            stu = models.User.objects.get(id = id)
            action = models.workf.objects.create(creator_id=id,title=request.params['submitdata'][0]['value'],currentstate=now_state,teacher=stu.teacherid)
            step = models.steps.objects.create(actionname = actionname,nextstate = now_state,operator_id=id,work_id=action.id,key=request.params['key'])
            datas = request.params['submitdata']
            for data in datas:
                models.submitdata.objects.create(name=data['name'], type=data['type'], data=data['value'],
                                                       step_id=step.id)

    elif key == 'approve_topic':
        actionname = '批准主题'
        next_state = '主题已通过'
        with transaction.atomic():
            work = models.workf.objects.get(id = request.params['wf_id'])
            work.currentstate = next_state
            work.save()
            step = models.steps.objects.create(actionname=actionname, nextstate=next_state, operator_id=id,
                                               work_id=work.id, key=request.params['key'])
            datas = request.params['submitdata']
            for data in datas:
                models.submitdata.objects.create(name=data['name'], type=data['type'], data=data['value'],
                                                       step_id=step.id)

    elif key == 'reject_topic':
        actionname = '驳回主题'
        next_state = '主题被驳回'
        with transaction.atomic():
            work = models.workf.objects.get(id=request.params['wf_id'])
            work.currentstate = next_state
            work.save()
            step = models.steps.objects.create(actionname=actionname, nextstate=next_state, operator_id=id,
                                               work_id=work.id, key=request.params['key'])
            datas = request.params['submitdata'][0]
            models.submitdata.objects.create(name=datas['name'], type=datas['type'], data=datas['value'],
                                                       step_id=step.id)

    elif key == 'submit_design':
        actionname = '毕业设计内容'
        next_state = '学生已提交毕业设计'
        with transaction.atomic():
            work = models.workf.objects.get(id=request.params['wf_id'])
            work.currentstate = next_state
            work.save()
            step = models.steps.objects.create(actionname=actionname, nextstate=next_state, operator_id=id,
                                               work_id=work.id, key=request.params['key'])
            datas = request.params['submitdata'][0]
            models.submitdata.objects.create(name=datas['name'], type=datas['type'], data=datas['value'],
                                                   step_id=step.id)

    elif key == 'modify_topic':
        actionname = '修改主题'
        next_state = '主题已创建'
        with transaction.atomic():
            work = models.workf.objects.get(id=request.params['wf_id'])
            work.currentstate = next_state
            work.save()
            step = models.steps.objects.create(actionname=actionname, nextstate=next_state, operator_id=id,
                                               work_id=work.id, key=request.params['key'])
            datas = request.params['submitdata']
            for data in datas:
                models.submitdata.objects.create(name=data['name'], type=data['type'], data=data['value'],
                                                 step_id=step.id)
    elif key == 'score_design':
        actionname = '毕业设计评分'
        next_state = '已评分'
        with transaction.atomic():
            work = models.workf.objects.get(id=request.params['wf_id'])
            work.currentstate = next_state
            work.save()
            step = models.steps.objects.create(actionname=actionname, nextstate=next_state, operator_id=id,
                                               work_id=work.id, key=request.params['key'])
            datas = request.params['submitdata']
            for data in datas:
                models.submitdata.objects.create(name=data['name'], type=data['type'], data=data['value'],
                                                     step_id=step.id)
    elif key == 'reject':
        actionname = '打回重做'
        next_state = '主题已通过'
        with transaction.atomic():
            work = models.workf.objects.get(id=request.params['wf_id'])
            work.currentstate = next_state
            work.save()
            step = models.steps.objects.create(actionname=actionname, nextstate=next_state, operator_id=id,
                                               work_id=work.id, key=request.params['key'])
            datas = request.params['submitdata']
            for data in datas:
                models.submitdata.objects.create(name=data['name'], type=data['type'], data=data['value'],
                                                 step_id=step.id)
    return JsonResponse({"ret": 0, "wf_id": step.id})


def more(request):
    id = request.params['step_id']
    data = models.submitdata.objects.filter(step_id = id).annotate(value=F('data')).values('type','name','value')
    data = list(data)
    return JsonResponse({'ret': 0, 'data': data})
