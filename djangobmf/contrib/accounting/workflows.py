#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from djangobmf.workflows import Workflow, State, Transition

from .tasks import bmfcontrib_accounting_calc_balance


class TransactionWorkflow(Workflow):
    class States:
        open = State(_(u"Open"), True, delete=False)
        balanced = State(_(u"Balanced"), update=False, delete=False)
        cancelled = State(_(u"Cancelled"), update=False, delete=False)

    class Transitions:
        balance = Transition(_("Balance"), "open", "balanced")
        cancel = Transition(_("Cancel"), "open", "cancelled", validate=False)

    def balance(self):
        if not self.instance.is_balanced():
            raise ValidationError(_('The transaction is not balanced'))

        self.instance.items.update(draft=False)

        for item in self.instance.items.all():
            bmfcontrib_accounting_calc_balance(item.account_id)

        # Update accounts
        self.instance.draft = False
