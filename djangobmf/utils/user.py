#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.apps import apps

from djangobmf.conf import settings


def user_add_bmf(user):
    """
    Adds ``djangobmf_employee`` and ``djangobmf_teams`` to the given
    user instance.
    """

    if not hasattr(user, 'djangobmf_employee'):
        try:
            employee = apps.get_model(settings.CONTRIB_EMPLOYEE)
            try:
                setattr(
                    user,
                    'djangobmf_employee',
                    employee.objects.get(user=user)
                )
            except employee.DoesNotExist:
                setattr(user, 'djangobmf_employee', None)

            setattr(user, 'djangobmf_has_employee', True)

        except LookupError:
            setattr(user, 'djangobmf_employee', None)
            setattr(user, 'djangobmf_has_employee', False)

    if not hasattr(user, 'djangobmf_teams'):
        try:
            teams = apps.get_model(settings.CONTRIB_TEAM)
            setattr(
                user,
                'djangobmf_teams',
                teams.objects.filter(members=getattr(user, 'djangobmf_employee')).values_list("id", flat=True),
            )
        except LookupError:
            setattr(user, 'djangobmf_teams', [])
