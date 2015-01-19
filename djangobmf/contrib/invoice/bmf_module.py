#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from djangobmf.categories import BaseCategory
from djangobmf.categories import ViewFactory
from djangobmf.categories import Accounting
from djangobmf.sites import site

from .models import Invoice
from .models import InvoiceProduct
from .views import InvoiceCreateView
from .views import InvoiceUpdateView


site.register_module(Invoice, **{
    'create': InvoiceCreateView,
    'update': InvoiceUpdateView,
    'report': True,
})


site.register_module(InvoiceProduct, **{
})


class InvoiceCategory(BaseCategory):
    name = _('Invoices')
    slug = "invoices"


site.register_dashboards(
    Accounting(
        InvoiceCategory(
            ViewFactory(
                model=Invoice,
                name=_("Open invoices"),
                slug="open",
                manager="open",
            ),
            ViewFactory(
                model=Invoice,
                name=_("All invoices"),
                slug="all",
                date_resolution="month",
            ),
        ),
    ),
)
