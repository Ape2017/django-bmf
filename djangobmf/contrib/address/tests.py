#!/usr/bin/python
# ex:set fileencoding=utf-8:
# flake8: noqa
# pragma: no cover

from __future__ import unicode_literals

from .models import Address
from djangobmf.utils.testcases import BaseTestCase
from djangobmf.utils.testcases import ModuleMixin

class AddressModuleTests(ModuleMixin, BaseTestCase):

    def test_urls_user(self):
        """
        """
        self.model = Address

        data = self.autotest_ajax_get('create', kwargs={'key': 'default'})
        data = self.autotest_ajax_post('create', kwargs={'key': 'default'}, data={
            'customer': 1,
            'name': 'name',
            'street': 'street 12',
            'zip': '24342',
            'city': 'city',
            'state': 'state',
            'country': 'country',
            'is_active': '1',
        })
        self.assertNotEqual(data["object_pk"], 0)
#       self.autotest_get('index', 200)

        obj = self.get_latest_object()
        a = '%s'%obj # check if object name has any errors

        self.autotest_get('detail', kwargs={'pk': obj.pk}, api=False)
        data = self.autotest_ajax_get('update', kwargs={'pk': obj.pk})
        self.autotest_get('delete', kwargs={'pk': obj.pk})
        self.autotest_post('delete', status_code=302, kwargs={'pk': obj.pk})
