"""
ueditor 管理面板模块
@author Peter
@time 20180814
"""

from __future__ import absolute_import
from django.db import models
from django.contrib.admin.widgets import AdminTextareaWidget
from .widgets import UEditor, AdminUEditor

__all__ = ['UEditorField', 'UEditor']


class UEditorField(models.TextField):
    """
    A text area model field for HTML content.

    It uses the TinyMCE 4 widget in forms.

    Example::

        from django.db.models import Model
        from tinymce import HTMLField

        class Foo(Model):
            html_content = HTMLField('HTML content')
    """

    def __init__(self, *args, **kwargs):
        self.ueditor_profile = kwargs.pop('profile', None)
        super(UEditorField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'widget': UEditor(profile=self.ueditor_profile)
        }
        defaults.update(kwargs)
        # As an ugly hack, we override the admin widget
        if defaults['widget'] == AdminTextareaWidget:
            defaults['widget'] = AdminUEditor(profile=self.ueditor_profile)
        return super(UEditorField, self).formfield(**defaults)
