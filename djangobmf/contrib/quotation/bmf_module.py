#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from djangobmf.categories import BaseCategory
from djangobmf.categories import ViewFactory
from djangobmf.categories import Sales
from djangobmf.sites import site

from .models import Quotation
from .models import QuotationProduct
from .views import QuotationCreateView
from .views import QuotationUpdateView


site.register_module(Quotation, **{
    'create': QuotationCreateView,
    'update': QuotationUpdateView,
    'report': True,
})


site.register_module(QuotationProduct, **{
})


class QuotationCategory(BaseCategory):
    name = _('Quotations')
    slug = "quotations"


site.register_dashboards(
    Sales(
        QuotationCategory(
            ViewFactory(
                model=Quotation,
                name=_("Open quotations"),
                slug="open",
                manager="open",
            ),
            ViewFactory(
                model=Quotation,
                name=_("All quotations"),
                slug="all",
            ),
        ),
    ),
)
