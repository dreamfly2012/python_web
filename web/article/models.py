from django.db import models
from ueditor import UEditorField

# Create your models here.
class article(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=20,default='')
    content = UEditorField('content',default='')
    date  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class access(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length = 100)
    shorturl = models.CharField(max_length=10,default='')
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.url

class comment(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length = 100)
    email = models.CharField(max_length=20,default='')
    content = models.TextField(max_length=5000,default='')
    date = models.DateTimeField(auto_now=True)
    article = models.ForeignKey(article,on_delete=models.CASCADE,related_name='comment_article',default='')
    def __str__(self):
        return self.name