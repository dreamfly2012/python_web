from django.shortcuts import render

from django.http import HttpResponse

from .forms import CommentForm

from article.models import comment

from article.models import article

from django.db.models import Q,F

import logging




from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.http import JsonResponse  
from django.core import serializers


logger = logging.getLogger('web')

def opdb(request):
    #info = article.objects.all()
    #info = article.objects.get(id=3)
    #info = article.objects.filter(title__startswith='a')
    #info = article.objects.filter(title='aa')
    #info = article.objects.filter(title='aa').values('title','author')
    #info = article.objects.all().values('title','author')
    #info = article.objects.filter(title__startswith='a').filter(author='我')
    #info = article.objects.filter(content__contains='我')
    #info = article.objects.last()
    #info  = article.objects.all()[2:4]
    #info = article.objects.filter(Q(title__startswith='a')|Q(author='我'))
    #info = article.objects.filter(id=1).update(content='1')
    #info = article.objects.filter(id=1).update(content=F('author'))
    #info = article.objects.order_by('-id').all()
    #info = article.objects.order_by('id').all().reverse()
    info = article.objects.raw('select * from article_article where id = 2')
    #info = info.comment_article.all()
    info = info[0].title
    print(info)

    return HttpResponse('Hello world')

@csrf_exempt
def interface(request):
    print(request.method)
    if(request.method=='GET'):
        context = {}
        return render(request, 'index/interface.html',context)
    else:
        context = {}
        context['articles'] = article.objects.filter(title='aa')
        print(context)
        context = serializers.serialize("json",article.objects.filter(title='aa'))
        return JsonResponse(context,safe=False)
      
       

# Create your views here.
def page_not_found(request,exception):
    return render(request,'index/404.html')    

def index(request):
    logger.debug('debug log')
    logger.info('info log')
    context = {}
    context['articles'] = article.objects.filter(title='aa')
    context['form'] =  CommentForm()
    return render(request, 'index/index.html',context)

def postcomment(request):
    if(request.method=='POST'):
        info  = request.POST
        #db = comment(name='ss', email='ss', content='ss')
        db = comment(name=info['name'],email=info['email'],content=info['content'])
        db.save()
        context = {}
        context['name'] = info['name']
        context['content'] = info['content']
        return render(request,'index/comment.html',context)

def update(request):
    db = article.objects.first()
    db.title = 'bb'
    db.save()
    return HttpResponse("hello world")

def new(request):
    article = articles(title='我是谁', content='我在那里',author='我')
    article.save()

    return HttpResponse('ok')

def show(request):
    context = {}
    context['title'] = "course"
    context['courses'] = ['php','java','python','go','nodejs']
    return render(request, 'index/show.html',context)    



