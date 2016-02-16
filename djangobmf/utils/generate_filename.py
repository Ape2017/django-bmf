#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.utils.text import get_valid_filename
from django.utils.timezone import now
from django.utils.encoding import force_text
from django.utils.encoding import smart_str

from djangobmf.conf import settings

import uuid
import os


def generate_filename(instance, filename, uuidfunction=uuid.uuid4):
    prefix = []
    if getattr(instance, 'is_static', False):
        prefix.append(settings.DOCUMENT_STATIC_PREFIX)
        if getattr(instance, 'content_type', None):
            prefix.append('%s' % instance.content_type.name)
            if getattr(instance, 'content_id'):
                prefix.append('%s' % instance.content_id)
    else:
        uuid_str = str(uuidfunction())
        prefix.append(force_text(now().strftime(smart_str("%Y"))))
        prefix.append(force_text(now().strftime(smart_str("%m"))))
        prefix.append(uuid_str[0:2])
        prefix.append(uuid_str[2:4])
        prefix.append(uuid_str[4:])
    prefix.append(get_valid_filename(filename))
    return os.path.join(*prefix)
