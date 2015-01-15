#!/usr/bin/python
# ex:set fileencoding=utf-8:
# flake8: noqa

from __future__ import unicode_literals

from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse

from factory.django import DjangoModelFactory
from unittest import expectedFailure

from .models import Invoice
from djangobmf.utils.testcases import BaseTestCase
from djangobmf.utils.testcases import ModuleMixin
# from djangobmf.utils.testcases import WorkflowTestCase


class InvoiceFactory(DjangoModelFactory):
    class Meta:
        model = Invoice
   #customer = 1
   #project = 1
   #date = '2014-01-01'
   #invoice_address = 1
   #shipping_address = 1
   #employee = 1
   #invoice_number = "TEST INVOICE"


class InvoiceModuleTests(ModuleMixin, BaseTestCase):

    def test_urls_user(self):
        """
        """
        self.model = Invoice

        data = self.autotest_ajax_get('create', kwargs={'key': 'default'})
       #data = self.autotest_ajax_post('create', data={
       #})
       #data = self.autotest_get('index')


#@expectedFailure
#class InvoiceWorkflowTests(WorkflowTestCase):
#    pass

   #def test_invoice_workflow(self):
   #    self.object = InvoiceFactory()
   #    workflow = self.workflow_build()
   #    workflow = self.workflow_autotest()
