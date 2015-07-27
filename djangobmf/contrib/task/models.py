#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from djangobmf.conf import settings
from djangobmf.models import BMFModel

from .workflows import GoalWorkflow
from .workflows import TaskWorkflow

from math import floor


class GoalManager(models.Manager):
    def get_queryset(self):
        return super(GoalManager, self) \
            .get_queryset() \
            .select_related('project')


@python_2_unicode_compatible
class AbstractGoal(BMFModel):
    """
    """
    summary = models.CharField(_("Title"), max_length=255, null=True, blank=False, )
    description = models.TextField(_("Description"), null=True, blank=True, )

    project = models.ForeignKey(  # TODO: make optional
        settings.CONTRIB_PROJECT, null=True, blank=True, on_delete=models.CASCADE,
    )

    referee = models.ForeignKey(
        settings.CONTRIB_EMPLOYEE, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+"
    )
    team = models.ForeignKey(
        settings.CONTRIB_TEAM, null=True, blank=True, on_delete=models.SET_NULL,
    )
    employees = models.ManyToManyField(
        settings.CONTRIB_EMPLOYEE, blank=True,
        related_name="employees"
    )

    completed = models.BooleanField(_("Completed"), default=False, editable=False)

    objects = GoalManager()

    class Meta(BMFModel.Meta):  # only needed for abstract models
        verbose_name = _('Goal')
        verbose_name_plural = _('Goals')
        ordering = ['project__name', 'summary']
        abstract = True
        permissions = (
            ('can_manage', 'Can manage all goals'),
        )
        swappable = "BMF_CONTRIB_GOAL"

    def bmfget_customer(self):
        if self.project:
            return self.project.customer
        return None

    def bmfget_project(self):
        return self.project

    @staticmethod
    def bmfrelated_project_queryset(qs):
        return qs.filter(completed=False)

    def __str__(self):
        return '%s' % (self.summary)

    def get_states(self):
        active_states = 0
        states = {
            "hold": 0.,
            "review": 0.,
            "done": 0.,
            "todo": 0.,
        }

        for state, count in self.task_set.values_list('state').annotate(count=models.Count('state')).order_by():
            if state in ["new", "open", ]:
                active_states += count

            if state in ["hold", ]:
                states["hold"] += count
                active_states += count

            if state in ["todo", "started"]:
                states["todo"] += count
                active_states += count

            if state in ["review", ]:
                states["review"] += count
                active_states += count

            if state in ["finished", ]:
                states["done"] += count
                active_states += count

        if active_states == 0:
            return states

        states['hold'] = '%4.2f' % (floor(10000 * states["hold"] / active_states) / 100)
        states['done'] = '%4.2f' % (floor(10000 * states["done"] / active_states) / 100)
        states['todo'] = '%4.2f' % (floor(10000 * states["todo"] / active_states) / 100)
        states['review'] = '%4.2f' % (floor(10000 * states["review"] / active_states) / 100)

        return states

    class BMFMeta:
        has_logging = False
        workflow = GoalWorkflow
        can_clone = True


class Goal(AbstractGoal):
    pass


class TaskManager(models.Manager):
    def get_queryset(self):
        related = ['goal', 'project']
        return super(TaskManager, self).get_queryset() \
            .annotate(due_count=models.Count('due_date')) \
            .order_by('-due_count', 'due_date', 'summary') \
            .select_related(*related)


@python_2_unicode_compatible
class AbstractTask(BMFModel):
    """
    """

    summary = models.CharField(_("Title"), max_length=255, null=True, blank=False)
    description = models.TextField(_("Description"), null=True, blank=True)
    due_date = models.DateField(_('Due date'), null=True, blank=True)

    project = models.ForeignKey(  # TODO: make optional
        settings.CONTRIB_PROJECT, null=True, blank=True, on_delete=models.CASCADE,
    )
    employee = models.ForeignKey(
        settings.CONTRIB_EMPLOYEE, null=True, blank=True, on_delete=models.SET_NULL,
    )
    in_charge = models.ForeignKey(
        settings.CONTRIB_EMPLOYEE, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", editable=False,
    )

    goal = models.ForeignKey(settings.CONTRIB_GOAL, null=True, blank=True, on_delete=models.CASCADE)

    completed = models.BooleanField(_("Completed"), default=False, editable=False)

    objects = TaskManager()

    class Meta(BMFModel.Meta):  # only needed for abstract models
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')
        ordering = ['due_date', 'summary']
        abstract = True
        swappable = "BMF_CONTRIB_TASK"

    def __str__(self):
        return '#%s: %s' % (self.pk, self.summary)

    def clean(self):
        # overwrite the project with the goals project
        if self.goal:
            self.project = self.goal.project

    def get_project_queryset(self, qs):
        if self.goal:
            return qs.filter(goal=self.goal)
        else:
            return qs

    def get_goal_queryset(self, qs):
        if self.project:
            return qs.filter(project=self.project)
        else:
            return qs

    def due_days(self):
        if self.due_date:
            time = now().date()
            if time >= self.due_date:
                return 0
            return (self.due_date - time).days

    class BMFMeta:
        workflow = TaskWorkflow
        has_files = True
        has_comments = True


class Task(AbstractTask):
    pass
