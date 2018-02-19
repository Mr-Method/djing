# coding=utf-8
from json import dumps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView
from django.utils.translation import ugettext as _
from django.conf import settings

from datetime import datetime

from django.views.generic.edit import FormMixin, DeleteView, UpdateView
from guardian.decorators import permission_required_or_403 as permission_required
from chatbot.models import MessageQueue
from abonapp.models import Abon
from .handle import TaskException
from .models import Task, ExtraComment
from mydefs import only_admins, safe_int, MultipleException, RuTimedelta
from .forms import TaskFrm, ExtraCommentForm


class BaseTaskListView(ListView):
    http_method_names = ['get']
    paginate_by = getattr(settings, 'PAGINATION_ITEMS_PER_PAGE', 10)


@method_decorator([login_required, only_admins], name='dispatch')
class NewTasksView(BaseTaskListView):
    """
    Show new tasks
    """
    template_name = 'taskapp/tasklist.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.filter(recipients=self.request.user, state='S') \
                           .select_related('abon', 'abon__street', 'abon__group', 'author')


class FailedTasksView(NewTasksView):
    """
    Show crashed tasks
    """
    template_name = 'taskapp/tasklist_failed.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.filter(recipients=self.request.user, state='C') \
                           .select_related('abon', 'abon__street', 'abon__group', 'author')


class FinishedTaskListView(NewTasksView):
    template_name = 'taskapp/tasklist_finish.html'

    def get_queryset(self):
        return Task.objects.filter(recipients=self.request.user, state='F') \
                           .select_related('abon', 'abon__street', 'abon__group', 'author')


class OwnTaskListView(NewTasksView):
    template_name = 'taskapp/tasklist_own.html'

    def get_queryset(self):
        # Attached and not finished tasks
        return Task.objects.filter(author=self.request.user)\
                           .exclude(state='F')\
                           .select_related('abon', 'abon__street', 'abon__group')


class MyTaskListView(NewTasksView):
    template_name = 'taskapp/tasklist.html'

    def get_queryset(self):
        # Tasks in which I participated
        return Task.objects.filter(recipients=self.request.user) \
                           .select_related('abon', 'abon__street', 'abon__group', 'author')


@method_decorator([login_required, permission_required('taskapp.can_viewall')], name='dispatch')
class AllTasksListView(BaseTaskListView):
    template_name = 'taskapp/tasklist_all.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.select_related('abon', 'abon__street', 'abon__group', 'author')


@login_required
@permission_required('taskapp.delete_task')
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    # prevent to delete task that assigned to me
    if request.user.is_superuser or request.user not in task.recipients.all():
        task.delete()
    else:
        messages.warning(request, _('You cannot delete task that assigned to you'))
    return redirect('taskapp:home')


@method_decorator([login_required, only_admins], name='dispatch')
class TaskUpdateView(UpdateView):
    http_method_names = ['get', 'post']
    template_name = 'taskapp/add_edit_task.html'
    form_class = TaskFrm
    context_object_name = 'task'

    def get_object(self, queryset=None):
        task_id = safe_int(self.kwargs.get('task_id'))
        if task_id == 0:
            return
        else:
            task = get_object_or_404(Task, pk=task_id)
            setattr(self, 'selected_abon', task.abon)
            return task

    def dispatch(self, request, *args, **kwargs):
        task_id = safe_int(self.kwargs.get('task_id', 0))
        if task_id == 0:
            if not request.user.has_perm('taskapp.add_task'):
                raise PermissionDenied
        else:
            if not request.user.has_perm('taskapp.change_task'):
                raise PermissionDenied
        return super(TaskUpdateView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        task_instance = form.save()
        self.object = task_instance
        selected_abon = task_instance.abon
        setattr(self, 'selected_abon', selected_abon)
        if selected_abon:
            # fetch profiles that has been attached on group of selected subscriber
            profiles = selected_abon.group.profiles.filter(is_active=True).filter(is_admin=True)
            if profiles.count() > 0:
                profile_ids = [prof.id for prof in profiles]
                task_instance.recipients.add(*profile_ids)
                task_instance.save()
                messages.add_message(self.request, messages.SUCCESS, _('Task has changed successfully'))
            else:
                messages.add_message(self.request, messages.ERROR, _('No responsible employee for the users group'))
        else:
            messages.add_message(self.request, messages.ERROR, _('You must select the subscriber'))
        return super(TaskUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        uid = safe_int(self.kwargs.get('uid'))
        selected_abon = getattr(
            self,
            'selected_abon',
            Abon.objects.get(username=str(uid)) if uid != 0 else None
        )

        now_date = datetime.now().date()
        task = self.object
        if task:
            if task.out_date > now_date:
                time_diff = "%s: %s" % (_('time left'), RuTimedelta(task.out_date - now_date))
            else:
                time_diff = _("Expired timeout -%(time_left)s") % {'time_left': RuTimedelta(now_date - task.out_date)}
        else:
            time_diff = None

        context = {
            'selected_abon': selected_abon,
            'time_diff': time_diff,
            'comments': ExtraComment.objects.filter(task=task),
            'comment_form': ExtraCommentForm()
        }
        context.update(kwargs)
        return super(TaskUpdateView, self).get_context_data(**context)

    def get_success_url(self):
        task_id = safe_int(self.kwargs.get('task_id'))
        if task_id == 0:
            return resolve_url('taskapp:own_tasks')
        else:
            return resolve_url('taskapp:edit', task_id)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, _('fix form errors'))
        return super(TaskUpdateView, self).form_invalid(form)


@login_required
@only_admins
def task_finish(request, task_id):
    try:
        task = get_object_or_404(Task, id=task_id)
        task.finish(request.user)
    except MultipleException as errs:
        for err in errs.err_list:
            messages.add_message(request, messages.constants.ERROR, err)
    except TaskException as e:
        messages.error(request, e)
    return redirect('taskapp:home')


@login_required
@only_admins
def task_failed(request, task_id):
    try:
        task = get_object_or_404(Task, id=task_id)
        task.do_fail(request.user)
    except TaskException as e:
        messages.error(request, e)
    return redirect('taskapp:home')


@login_required
@permission_required('taskapp.can_remind')
def remind(request, task_id):
    try:
        task = get_object_or_404(Task, id=task_id)
        task.save(update_fields=['state'])
    except MultipleException as errs:
        for err in errs.err_list:
            messages.add_message(request, messages.constants.ERROR, err)
    except TaskException as e:
        messages.error(request, e)
    return redirect('taskapp:home')


def check_news(request):
    if request.user.is_authenticated and request.user.is_admin:
        msg = MessageQueue.objects.pop(user=request.user, tag='taskap')
        if msg is not None:
            r = {
                'auth': True,
                'exist': True,
                'content': msg,
                'title': _('Task')
            }
        else:
            r = {'auth': True, 'exist': False}
    else:
        r = {'auth': False}
    return HttpResponse(dumps(r))


@method_decorator([login_required, only_admins], name='dispatch')
@method_decorator(permission_required('taskapp.add_extracomment'), name='dispatch')
class NewCommentView(CreateView):
    form_class = ExtraCommentForm
    http_method_names = ['get', 'post']

    def get_success_url(self):
        task_id = self.kwargs.get('task_id')
        return resolve_url('taskapp:edit', task_id)

    def form_valid(self, form):
        self.task = get_object_or_404(Task, pk=self.kwargs.get('task_id'))
        self.object = form.make_save(
            author=self.request.user,
            task=self.task
        )
        return FormMixin.form_valid(self, form)


@method_decorator([login_required, only_admins], name='dispatch')
@method_decorator(permission_required('taskapp.delete_extracomment'), name='dispatch')
class DeleteCommentView(DeleteView):
    model = ExtraComment
    pk_url_kwarg = 'comment_id'
    http_method_names = ['get', 'post']
    template_name = 'taskapp/comments/extracomment_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = {
            'task_id': self.kwargs.get('task_id')
        }
        context.update(kwargs)
        return super(DeleteCommentView, self).get_context_data(**context)

    def get_success_url(self):
        task_id = self.kwargs.get('task_id')
        return resolve_url('taskapp:edit', task_id)
