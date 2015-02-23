#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from .module import ModuleListView
from .module import ModuleCloneView
from .module import ModuleCreateView
from .module import ModuleDeleteView
from .module import ModuleDetailView
from .module import ModuleFormAPI
from .module import ModuleReportView
from .module import ModuleUpdateView
from .module import ModuleWorkflowView

from .interface import ModuleOverviewView

from .mixins import ModuleViewMixin


__all__ = (
    'ModuleListView',
    'ModuleCloneView',
    'ModuleCreateView',
    'ModuleDeleteView',
    'ModuleDetailView',
    'ModuleFormAPI',
    'ModuleReportView',
    'ModuleUpdateView',
    'ModuleWorkflowView',
    'ModuleViewMixin',
    'ModuleOverviewView',
)
