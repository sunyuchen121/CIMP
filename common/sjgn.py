
import json
from django.contrib.auth import login,logout,authenticate
from django.http import JsonResponse
def sign(request):
    request.params = json.loads(request.body)
    action = request.params['action']
    if action == 'signin':
        return signin(request)
    elif action == 'signout':
        return signout(request)
def signin(request):
    username = request.params['username']
    password = request.params['password']
    user = authenticate(username=username,password=password)#如果校验通过则返回user对象，如果校验不通过则返回None
    if user is not None:
        if user.is_active:
            login(request,user)
            request.session['usertype']=user.usertype
            request.session['id']=user.id
            return JsonResponse({'ret':0,'usertype':user.usertype,"userid":user.id,"realname":user.realname})
        else:
            return JsonResponse({'ret':1,'msg':'用户已被封禁'})
    else:
        return JsonResponse({'ret':1,'msg':'用户名或密码错误'})

def signout(request):
    request.session.flush()
    logout(request)
    return JsonResponse({'ret': 0})