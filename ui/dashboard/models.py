from django.contrib.auth.models import User

from ui import models

class Todo(models.Model):
    user = models.ForeignKey(User)
    checked = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    text = models.CharField(max_length=700)
    created = models.DateTimeField(auto_now_add=True)

