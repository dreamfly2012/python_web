# coding: utf-8
# License: MIT, see LICENSE.txt

from __future__ import absolute_import
import re
import sys
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage


def is_managed():
    """
    Check if a Django project is being managed with ``manage.py`` or
    ``django-admin`` scripts
    :return: Check result
    :rtype: bool
    """
    for item in sys.argv:
        if re.search(r'manage.py|django-admin|django', item) is not None:
            return True
    return False


# settings.configure()
STATIC_URL = '/static/'
DEFAULT = {}
CONFIG = getattr(settings, 'UEDITOR_DEFAULT_CONFIG', DEFAULT)
CONFIG_URL = staticfiles_storage.url('/ueditor/ueditor.config.js')
JS_URL = getattr(settings, 'UEDITOR_JS_URL', None)
USE_SPELLCHECKER = False
if JS_URL is None:
    JS_URL = staticfiles_storage.url('ueditor/ueditor.all.min.js')
