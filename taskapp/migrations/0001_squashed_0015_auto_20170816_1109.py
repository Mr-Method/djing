# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-09-05 12:23
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import taskapp.models


class Migration(migrations.Migration):

    replaces = [('taskapp', '0001_initial'), ('taskapp', '0002_auto_20161006_0027'), ('taskapp', '0003_auto_20161130_1815'), ('taskapp', '0004_auto_20161202_1230'), ('taskapp', '0005_auto_20161206_0013'), ('taskapp', '0006_auto_20161206_2135'), ('taskapp', '0007_auto_20161206_2303'), ('taskapp', '0008_auto_20161213_1932'), ('taskapp', '0009_auto_20161216_2214'), ('taskapp', '0010_auto'), ('taskapp', '0011_auto_20170116_0126'), ('taskapp', '0012_auto_20170407_0124'), ('taskapp', '0013_auto_20170413_1944'), ('taskapp', '0014_auto_20170416_1029'), ('taskapp', '0015_auto_20170816_1109')]

    initial = True

    dependencies = [
        ('devapp', '0001_squashed_0007_auto_20170816_1109'),
        ('abonapp', '0001_squashed_0022_auto_20170816_1109'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descr', models.CharField(max_length=128)),
                ('priority', models.CharField(choices=[('A', 'Высший'), ('B', 'Выше среднего'), ('C', 'Средний'), ('D', 'Ниже среднего'), ('E', 'Низкий')], default='C', max_length=1)),
                ('out_date', models.DateField(blank=True, default=taskapp.models._delta_add_days, null=True)),
                ('time_of_create', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dev', to='devapp.Device')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'task',
            },
        ),
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ('-id',)},
        ),
        migrations.AddField(
            model_name='task',
            name='state',
            field=models.CharField(choices=[('S', 'Новая'), ('C', 'На выполнении'), ('F', 'Выполнена')], default='S', max_length=1),
        ),
        migrations.AddField(
            model_name='task',
            name='attachment',
            field=models.ImageField(blank=True, null=True, upload_to='task_attachments/%Y.%m.%d'),
        ),
        migrations.AddField(
            model_name='task',
            name='mode',
            field=models.CharField(choices=[('na', 'не выбрано'), ('yt', 'жёлтый треугольник'), ('rc', 'красный крестик'), ('ls', 'слабая скорость'), ('cf', 'обрыв кабеля'), ('cn', 'подключение'), ('pf', 'переодическое пропадание'), ('cr', 'настройка роутера'), ('co', 'настроить onu'), ('fc', 'обжать кабель'), ('ot', 'другое')], default='na', max_length=2),
        ),
        migrations.AddField(
            model_name='task',
            name='abon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='abonapp.Abon'),
        ),
        migrations.AlterField(
            model_name='task',
            name='priority',
            field=models.CharField(choices=[('A', 'Высший'), ('C', 'Средний'), ('E', 'Низкий')], default='E', max_length=1),
        ),
        migrations.CreateModel(
            name='ChangeLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('act_type', models.CharField(choices=[('e', 'Изменение задачи'), ('c', 'Создание задачи'), ('d', 'Удаление задачи')], max_length=1)),
                ('when', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ('-id',), 'permissions': (('can_viewall', 'Доступ ко всем задачам'),)},
        ),
        migrations.AddField(
            model_name='changelog',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='taskapp.Task'),
        ),
        migrations.AddField(
            model_name='changelog',
            name='who',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RemoveField(
            model_name='task',
            name='device',
        ),
        migrations.RemoveField(
            model_name='task',
            name='recipient',
        ),
        migrations.AddField(
            model_name='task',
            name='recipients',
            field=models.ManyToManyField(related_name='them_task', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ('-id',), 'permissions': (('can_viewall', 'Доступ ко всем задачам'), ('can_remind', 'Напоминания о задачах'))},
        ),
        migrations.AlterField(
            model_name='changelog',
            name='act_type',
            field=models.CharField(choices=[('e', 'Изменение задачи'), ('c', 'Создание задачи'), ('d', 'Удаление задачи'), ('f', 'Завершение задачи'), ('b', 'Задача начата')], max_length=1),
        ),
        migrations.AlterField(
            model_name='task',
            name='descr',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='attachment',
            field=models.ImageField(blank=True, null=True, upload_to='media/task_attachments/%Y.%m.%d'),
        ),
        migrations.AlterField(
            model_name='task',
            name='attachment',
            field=models.ImageField(blank=True, null=True, upload_to='task_attachments/%Y.%m.%d'),
        ),
        migrations.AlterField(
            model_name='task',
            name='abon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='abonapp.Abon'),
        ),
        migrations.AlterField(
            model_name='task',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='changelog',
            name='act_type',
            field=models.CharField(choices=[('e', 'Изменение задачи'), ('c', 'Создание задачи'), ('d', 'Удаление задачи'), ('f', 'Завершение задачи'), ('b', 'Задача провалена')], max_length=1),
        ),
        migrations.AlterField(
            model_name='task',
            name='state',
            field=models.CharField(choices=[('S', 'Новая'), ('C', 'Провалена'), ('F', 'Выполнена')], default='S', max_length=1),
        ),
    ]