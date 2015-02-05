#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from django.utils.timezone import now
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from djangobmf.models import BMFModel
from djangobmf.settings import CONTRIB_PROJECT
from djangobmf.settings import CONTRIB_EMPLOYEE
from djangobmf.settings import CONTRIB_TEAM
from djangobmf.settings import CONTRIB_GOAL

from .workflows import GoalWorkflow
from .workflows import TaskWorkflow

from math import floor


class GoalManager(models.Manager):

    def get_queryset(self):
        return super(GoalManager, self) \
            .get_queryset() \
            .select_related('project')

    def active(self, request):
        return self.get_queryset().filter(
            completed=False,
        )

    def mygoals(self, request):
        return self.get_queryset().filter(
            completed=False,
            referee=getattr(request.user, 'djangobmf_employee', -1),
        )


@python_2_unicode_compatible
class AbstractGoal(BMFModel):
    """
    """
    summary = models.CharField(_("Title"), max_length=255, null=True, blank=False, )
    description = models.TextField(_("Description"), null=True, blank=True, )

    project = models.ForeignKey(  # TODO: make optional
        CONTRIB_PROJECT, null=True, blank=True, on_delete=models.CASCADE,
    )

    referee = models.ForeignKey(
        CONTRIB_EMPLOYEE, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+"
    )
    team = models.ForeignKey(
        CONTRIB_TEAM, null=True, blank=True, on_delete=models.SET_NULL,
    )
    employees = models.ManyToManyField(
        CONTRIB_EMPLOYEE, blank=True,
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

    @classmethod
    def has_permissions(cls, qs, user):
        if user.has_perm('%s.can_manage' % cls._meta.app_label, cls):
            return qs

        qs_filter = Q(referee=getattr(user, 'djangobmf_employee', -1))
        qs_filter |= Q(employees=getattr(user, 'djangobmf_employee', -1))
        qs_filter |= Q(team__in=getattr(user, 'djangobmf_teams', []))

        if hasattr(cls, "project"):
            project = cls._meta.get_field_by_name("project")[0].model
            if user.has_perm('%s.can_manage' % project._meta.app_label, project):
                qs_filter |= Q(project__isnull=False)
            else:
                qs_filter |= Q(project__isnull=False, project__employees=getattr(user, 'djangobmf_employee', -1))
                qs_filter |= Q(project__isnull=False, project__team__in=getattr(user, 'djangobmf_teams', []))
        return qs.filter(qs_filter)

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

    def active(self, request):
        return self.get_queryset().filter(
            completed=False,
        )

    def available(self, request):
        return self.get_queryset().filter(
            employee=None,
            completed=False,
        )

    def mytasks(self, request):
        return self.get_queryset().filter(
            completed=False,
            employee=getattr(request.user, 'djangobmf_employee', -1),
        )

    def todo(self, request):
        return self.get_queryset().filter(
            completed=False,
            state__in=["todo", "started", "review"],
            employee=getattr(request.user, 'djangobmf_employee', -1),
        )


@python_2_unicode_compatible
class AbstractTask(BMFModel):
    """
    """

    summary = models.CharField(_("Title"), max_length=255, null=True, blank=False)
    description = models.TextField(_("Description"), null=True, blank=True)
    due_date = models.DateField(_('Due date'), null=True, blank=True)

    project = models.ForeignKey(  # TODO: make optional
        CONTRIB_PROJECT, null=True, blank=True, on_delete=models.CASCADE,
    )
    employee = models.ForeignKey(
        CONTRIB_EMPLOYEE, null=True, blank=True, on_delete=models.SET_NULL,
    )
    in_charge = models.ForeignKey(
        CONTRIB_EMPLOYEE, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", editable=False,
    )

    goal = models.ForeignKey(CONTRIB_GOAL, null=True, blank=True, on_delete=models.CASCADE)

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

    @classmethod
    def has_permissions(cls, qs, user):
        qs_filter = Q(project__isnull=True, goal__isnull=True)
        qs_filter |= Q(employee=getattr(user, 'djangobmf_employee', -1))
        qs_filter |= Q(in_charge=getattr(user, 'djangobmf_employee', -1))

        if hasattr(cls, "goal"):
            goal = cls._meta.get_field_by_name("goal")[0].model
            if user.has_perm('%s.can_manage' % goal._meta.app_label, goal):
                qs_filter |= Q(goal__isnull=False)
            else:
                qs_filter |= Q(goal__isnull=False, goal__referee=getattr(user, 'djangobmf_employee', -1))
                qs_filter |= Q(goal__isnull=False, goal__employees=getattr(user, 'djangobmf_employee', -1))
                qs_filter |= Q(goal__isnull=False, goal__team__in=getattr(user, 'djangobmf_teams', []))

        if hasattr(cls, "project"):
            project = cls._meta.get_field_by_name("project")[0].model
            if user.has_perm('%s.can_manage' % project._meta.app_label, project):
                qs_filter |= Q(project__isnull=False)
            else:
                qs_filter |= Q(project__isnull=False, project__employees=getattr(user, 'djangobmf_employee', -1))
                qs_filter |= Q(project__isnull=False, project__team__in=getattr(user, 'djangobmf_teams', []))

        return qs.filter(qs_filter)

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
