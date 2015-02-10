#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from djangobmf.views import ModuleCloneView
from djangobmf.views import ModuleDetailView
from djangobmf.views import ModuleGetView

from .forms import GoalCloneForm


class GoalGetView(ModuleGetView):
    def get_item_data(self, data):
        l = []
        for d in data:
            l.append({
                'name': str(d),
                'completed': d.completed,
                'referee': str(d.referee),
                'project': str(d.project),
                'url': d.bmfmodule_detail(),
                'states': d.get_states(),
            })
        return l


class TaskGetView(ModuleGetView):
    pass


class GoalCloneView(ModuleCloneView):
    form_class = GoalCloneForm

    def clone_object(self, formdata, instance):
        instance.completed = False

    def clone_related_objects(self, formdata, old_object, new_object):
        if formdata['copy_tasks']:
            for task in old_object.task_set.all():
                task.pk = None
                task.goal = new_object
                task.project = new_object.project
                if formdata['clear_employee']:
                    task.employee = None
                task.due_date = None
                task.completed = False
                task.work_date = None
                task.seconds_on = 0
                setattr(
                    task,
                    task._bmfmeta.workflow_field_name,
                    task._bmfmeta.workflow.default
                )
                task.save()


class GoalDetailView(ModuleDetailView):
    def get_context_data(self, **kwargs):
        tasks = {
            'open': [],
            'hold': [],
            'done': [],
        }
        for task in self.object.task_set.all():
            if task.state in ["open", "started", "new"]:
                tasks["open"].append(task)
            elif task.state in ["hold", "review", "todo"]:
                tasks["hold"].append(task)
            else:
                tasks["done"].append(task)

        kwargs.update({
            'tasks': tasks,
        })
        return super(GoalDetailView, self).get_context_data(**kwargs)
