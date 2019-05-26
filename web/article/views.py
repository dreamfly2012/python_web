from django.shortcuts import render

from django.http import HttpResponse

from .forms import CommentForm

from article.models import comment

# Create your views here.

def index(request):
    from article.models import article
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
    from article.models import article
    db = article.objects.first()
    db.title = 'bb'
    db.save()
    return HttpResponse("hello world")

def new(request):
    from article.models import article
    article = article(title='我是谁', content='我在那里',author='我')
    article.save()

    return HttpResponse('ok')

def show(request):
    context = {}
    context['title'] = "course"
    context['courses'] = ['php','java','python','go','nodejs']
    return render(request, 'index/show.html',context)    



