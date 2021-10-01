from django.forms import ModelForm
from article.models import comment

class CommentForm(ModelForm):
    class Meta:
        model = comment
        fields = ['name','email','content']
