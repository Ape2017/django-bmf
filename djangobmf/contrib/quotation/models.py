#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from djangobmf.conf import settings
from djangobmf.models import BMFModel
from djangobmf.numbering.utils import numbercycle_get_name, numbercycle_delete_object
from djangobmf.fields import CurrencyField
from djangobmf.fields import MoneyField

import datetime
from decimal import Decimal

from .workflows import QuotationWorkflow


class QuotationManager(models.Manager):

    def open(self, request):
        return self.get_queryset().filter(
            # completed=False,
            state__in=['draft', 'send', 'accepted'],
        )


@python_2_unicode_compatible
class AbstractQuotation(BMFModel):
    """
    """
    invoice = models.OneToOneField(
        settings.CONTRIB_INVOICE,
        null=True,
        blank=True,
        editable=False,
        related_name="quotation",
        on_delete=models.PROTECT
    )
    customer = models.ForeignKey(  # TODO: make me optional
        settings.CONTRIB_CUSTOMER,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
    )
    project = models.ForeignKey(  # TODO: make me optional
        settings.CONTRIB_PROJECT,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
    )
    employee = models.ForeignKey(  # TODO: make me optional
        settings.CONTRIB_EMPLOYEE,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
    )
    shipping_address = models.ForeignKey(
        settings.CONTRIB_ADDRESS,
        null=True,
        blank=True,
        related_name="shipping_quotation",
        on_delete=models.PROTECT,
    )
    invoice_address = models.ForeignKey(
        settings.CONTRIB_ADDRESS,
        null=True,
        blank=True,
        related_name="invoice_quotation",
        on_delete=models.PROTECT,
    )
    quotation_number = models.CharField(_('Quotation number'), max_length=255, null=True, blank=False)
    products = models.ManyToManyField(
        settings.CONTRIB_PRODUCT,
        through='QuotationProduct',
        editable=False,
    )
    net = models.FloatField(editable=False, blank=True, null=True)
    date = models.DateField(_("Date"), null=True, blank=False)
    valid_until = models.DateField(_("Valid until"), null=True, blank=True)
    notes = models.TextField(_("Notes"), null=True, blank=True)
    term_of_payment = models.TextField(_("Term of payment"), blank=True, null=True)

    completed = models.BooleanField(_("Completed"), default=False, editable=False)

    objects = QuotationManager()

    def __init__(self, *args, **kwargs):
        super(AbstractQuotation, self).__init__(*args, **kwargs)
        self.taxes = {}

    def __str__(self):
        return '%s' % self.quotation_number

    def bmfget_customer(self):
        if hasattr(self, 'customer'):
            return self.customer
        return None

    def bmfget_project(self):
        if hasattr(self, 'project'):
            return self.project
        return None

    def clean(self):
        if self.project and not self.customer_id:
            self.customer = self.project.customer
        if self.customer and not self.project_id:
            self.project = self.customer.project
        if self.customer and not self.invoice_address_id:
            self.invoice_address = \
                self.customer.customer_address.filter(is_billing=True, default_billing=True).first()
        if self.customer and not self.shipping_address_id:
            self.shipping_address = \
                self.customer.customer_address.filter(is_shipping=True, default_shipping=True).first()
        if not self.date:
            self.date = datetime.datetime.now().date()

    def bmf_clean(self):
        self.net = self.calc_net()

    @staticmethod
    def post_save(sender, instance, created, raw, *args, **kwargs):
        if not instance.quotation_number:
            name = numbercycle_get_name(instance)
            instance._meta.model.objects.filter(pk=instance.pk).update(quotation_number=name)

    @staticmethod
    def post_delete(sender, instance, *args, **kwargs):
        numbercycle_delete_object(instance)

    def get_products(self):
        if not hasattr(self, '_cache_products'):
            self._cache_products = self.quotation_products.all().select_related('product')
        return self._cache_products

    def calc_net(self):
        val = Decimal(0)
        for item in self.get_products():
            val += item.calc_net()
        return val

    def calc_gross(self):
        val = Decimal(0)
        for item in self.get_products():
            val += item.calc_gross()
        return val

    def calc_taxes(self):
        t = {}
        for item in self.get_products():
            for tax, value in item.calc_taxes():
                if tax in t:
                    t[tax] += value
                else:
                    t[tax] = value
        return t.items()

    class Meta:
        verbose_name = _('Quotation')
        verbose_name_plural = _('Quotations')
        ordering = ['-pk']
        abstract = True
        swappable = "BMF_CONTRIB_QUOTATION"

    class BMFMeta:
        observed_fields = ['quotation_number', 'net', 'state']
        has_files = True
        has_comments = True
        clean = True
        number_cycle = "Q{year}/{month}-{counter:04d}"
        workflow = QuotationWorkflow


class Quotation(AbstractQuotation):
    pass


class QuotationProduct(BMFModel):
    quotation = models.ForeignKey(
        settings.CONTRIB_QUOTATION, null=True, blank=True,
        related_name="quotation_products", on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        settings.CONTRIB_PRODUCT, null=True, blank=True,
        related_name="quotation_products", on_delete=models.PROTECT,
    )
    name = models.CharField(_("Name"), max_length=255, null=True, blank=False)
    price_currency = CurrencyField()
    price_precision = models.PositiveSmallIntegerField(
        default=0, blank=True, null=True, editable=False,
    )
    price = MoneyField(_("Price"), blank=False)
    amount = models.FloatField(_("Amount"), null=True, blank=False, default=1.0)
    # unit = models.CharField() # TODO add units
    description = models.TextField(_("Description"), null=True, blank=True)

    class BMFMeta:
        only_related = True

    def calc_all(self):
        if hasattr(self, '_calcs'):
            return self._calcs
        self._calcs = self.product.calc_tax(self.amount, self.price)
        return self._calcs

    def calc_net_unit(self):
        return self.calc_all()[0]

    def calc_net(self):
        return self.calc_all()[1]

    def calc_gross(self):
        return self.calc_all()[2]

    def calc_taxes(self):
        return self.calc_all()[3]

    def clean(self):
        if self.product and not self.name:
            self.name = self.product.name
        if self.product and not self.price:
            self.price = self.product.price
