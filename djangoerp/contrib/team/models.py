#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from djangoerp.models import ERPModel
from djangoerp.settings import BASE_MODULE
from djangoerp.categories import HR


@python_2_unicode_compatible
class AbstractTeam(ERPModel):
    """
    """
    name = models.CharField(
        max_length=255, null=False, blank=False, editable=True,
    )
    members = models.ManyToManyField(
        BASE_MODULE["EMPLOYEE"], blank=True, related_name="team_members",
        limit_choices_to={'user__isnull': False}, through='TeamMember',
    )

    class Meta(ERPModel.Meta):  # only needed for abstract models
        verbose_name = _('Team')
        verbose_name_plural = _('Teams')
        ordering = ['name']
        abstract = True

    class ERPMeta:
        search_fields = ['name']
        has_logging = False
        category = HR

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    team = models.ForeignKey(
        BASE_MODULE["TEAM"], null=True, blank=True, related_name="+", on_delete=models.CASCADE,
    )
    employee = models.ForeignKey(
        BASE_MODULE["EMPLOYEE"], null=True, blank=True, related_name="+", on_delete=models.CASCADE,
    )
    is_manager = models.BooleanField(_("Is manager"), default=False)

    class Meta:
        unique_together = ("team", "employee")


class Team(AbstractTeam):
    pass
