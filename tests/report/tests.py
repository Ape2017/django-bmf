#!/usr/bin/python
# ex:set fileencoding=utf-8:
# flake8: noqa

from __future__ import unicode_literals

from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from djangobmf.models import Report

from djangobmf.utils.testcases import BaseTestCase

class CoreTests(BaseTestCase):
    pass

#   def test_reports(self):
#       """
#       """
#       model = get_model_from_cfg("QUOTATION")
#       namespace = model._bmfmeta.url_namespace
 
#       r = self.client.post(reverse(namespace + ':create'), {
#           'project': 0,
#           'customer': 0,
#           'date': '2012-01-01',
#           'employee': 0,
#           'bmf-products-TOTAL_FORMS': 1,
#           'bmf-products-INITIAL_FORMS': 0,
#           'bmf-products-MAX_NUM_FORMS': 1,
#           'bmf-products-0-product': 1,
#           'bmf-products-0-amount': 1,
#           'bmf-products-0-price': 100,
#           'bmf-products-0-name': "Service",
#       })
#       self.assertEqual(r.status_code, 302)
 
#       obj = model.objects.order_by('pk').last()
 
#       r = self.client.get(reverse(namespace + ':report', None, None, {'pk': obj.pk}))
#       self.assertEqual(r.status_code, 200)
#       self.assertEqual(r._headers['content-type'][1], "application/pdf")
 
#       report = Report.objects.get(contenttype=ContentType.objects.get_for_model(model))
#       report.delete()
 
#       r = self.client.get(reverse(namespace + ':report', None, None, {'pk': obj.pk}))
#       self.assertEqual(r.status_code, 200)
#       self.assertNotEqual(r._headers['content-type'][1], "application/pdf")
