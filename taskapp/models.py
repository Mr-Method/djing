# coding=utf-8
from __future__ import unicode_literals

from django.db import models
from djing import settings
from devapp.models import Device
from datetime import datetime, timedelta


TASK_PRIORITIES = (
    (b'A', u'Высший'),
    (b'B', u'Выше среднего'),
    (b'C', u'Средний'),
    (b'D', u'Ниже среднего'),
    (b'E', u'Низкий')
)


class Task(models.Model):
    descr = models.CharField(max_length=128)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    device = models.ForeignKey(Device, related_name='dev')
    priority = models.CharField(max_length=1, choices=TASK_PRIORITIES, default=TASK_PRIORITIES[2][0])
    out_date = models.DateField(null=True, blank=True, default=datetime.now()+timedelta(days=7))
    time_of_create = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.descr

    class Meta:
        db_table = 'task'

    def save_form(self, frm_instance, auth_user):
        cl = frm_instance.cleaned_data
        self.descr = cl['descr']
        self.recipient = cl['recipient']
        self.author = auth_user
        self.device = cl['device']
        self.priority = cl['priority']
        self.out_date = cl['out_date']