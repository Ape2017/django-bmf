#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from djangobmf.views import ModuleCreateView
from djangobmf.views import ModuleListView


class EmployeeIndexView(ModuleListView):
    name = _("All Employees")
    slug = "all"


class EmployeeCreateView(ModuleCreateView):
    def get_initial(self):
        # TODO: ADD a default product to settings and read the configuration here
        # if self.request.djangobmf_employee:
        #     self.initial.update({'product': self.request.bmfcore['company'].employee_product_id})
        return super(EmployeeCreateView, self).get_initial()
