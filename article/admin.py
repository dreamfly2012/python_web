from django.contrib import admin

# Register your models here.

from .models import article,access

admin.site.site_header = "后台管理系统"

@admin.register(access)
class MyAdmin(admin.ModelAdmin):
    pass


admin.site.register(article,MyAdmin)