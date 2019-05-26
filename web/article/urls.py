
from django.urls import path,include
from . import views

urlpatterns = [
   path('index',views.index,name='index'),
   path('comment',views.postcomment,name='comment'),
   path('show',views.show,name='show'),
   path('update',views.update,name='update'),
   path('new',views.new,name='new')
]
