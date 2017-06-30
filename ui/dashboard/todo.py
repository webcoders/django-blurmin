from django.http.response import HttpResponse
from django.views.generic.base import View

from ui.dashboard.models import Todo
from ui.views import BaseView


class ToDoListView(BaseView, View):
    def get(self, request, *args, **kwargs):
        if 'text' in request.GET:
            todo = Todo()
            todo.user = request.user
            todo.text = request.GET['text']
            todo.save()
        if 'delete' in request.GET:
            Todo.objects.get(user=request.user, id=request.GET['delete']).delete()
        if 'check' in request.GET:
            check = request.GET['check']
            if check == 'true':
                check = True
            else:
                check = False
            todo = Todo.objects.get(user=request.user, id=request.GET['id'])
            todo.checked = check
            todo.save()
        data = list(Todo.objects.filter(user=request.user).order_by('checked')[:20].values())

        return HttpResponse(self.serialize(data))
