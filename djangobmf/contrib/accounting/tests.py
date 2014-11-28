#!/usr/bin/python
# ex:set fileencoding=utf-8:
# flake8: noqa

from __future__ import unicode_literals

from .models import Account
from ...testcase import BMFModuleTestCase


class AccountModuleTests(BMFModuleTestCase):

    def test_get_urls(self):
        """
        """
        self.model = Account

        data = self.autotest_ajax_get('create', kwargs={'default': 'default'})
        data = self.autotest_ajax_post('create', kwargs={'default': 'default'}, data={
            'number': "1",
            'name': "account 1",
            'type': 50,
        })
        self.autotest_get('index', 200)

        obj = self.get_latest_object()
        a = '%s'%obj # check if object name has any errors

        self.autotest_get('detail', kwargs={'pk': obj.pk})
        data = self.autotest_ajax_get('update', kwargs={'pk': obj.pk})
        self.autotest_get('delete', kwargs={'pk': obj.pk})
        self.autotest_post('delete', status_code=302, kwargs={'pk': obj.pk})
