from django.forms import ModelForm
from .models import Todo

#new generic form that we need to use in example: creating todoObject form
class TodoForm(ModelForm):
    #specifying what model and what fields we want to work with
    class Meta:
        model = Todo
        #fields of what we want to show up
        fields = ['title', 'memo', 'important']


