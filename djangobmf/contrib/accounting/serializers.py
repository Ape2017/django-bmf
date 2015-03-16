#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from djangobmf.serializers import ModuleSerializer

from rest_framework import serializers

from .models import Account
from .models import Transaction
from .models import TransactionItem


class AccountSerializer(ModuleSerializer):
    balance_formatted = serializers.SerializerMethodField()

    def get_balance_formatted(self, obj):
        return '%s' % obj.balance

    class Meta:
        model = Account


class TransactionSerializer(ModuleSerializer):

    class Meta:
        model = Transaction


class TransactionItemSerializer(ModuleSerializer):

    class Meta:
        model = TransactionItem
