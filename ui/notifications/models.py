from __future__ import unicode_literals
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from ui import models as ui_models


class NotificationQuerySet(models.query.QuerySet):
    def unread(self):
        return self.filter(unread=True)

    def read(self):
        return self.filter(unread=False)

    def mark_all_as_read(self, recipient=None):
        qs = self.unread()
        if recipient:
            qs = qs.filter(recipient=recipient)
        return qs.update(unread=False)

    def mark_all_as_unread(self, recipient=None):
        qs = self.read()
        if recipient:
            qs = qs.filter(recipient=recipient)
        return qs.update(unread=True)

    class Meta:
        app_label = "notifications"


class Notification(models.Model):
    action_object_content_type = ui_models.ForeignKey(ContentType, blank=True, null=True,
                                                      related_name='notify_action_object')
    action_object_object_id = ui_models.CharField(max_length=255, blank=True, null=True)
    action_object = GenericForeignKey('action_object_content_type', 'action_object_object_id')
    timestamp = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=150)
    message = models.TextField()
    LEVELS = (('success', 'success'),
              ('info', 'info'),
              ('warning', 'warning'),
              ('error', 'error'),)
    level = models.CharField(choices=LEVELS, default='s', max_length=20)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)


class NotificationRecipient(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, related_name='notifications')
    unread = models.BooleanField(default=True, blank=False)
    objects = NotificationQuerySet.as_manager()
    notification = models.ForeignKey(Notification)

    class Meta:
        app_label = "notifications"