from django.contrib import admin

from . import models


class UserDomainSelectorsAdmin(admin.ModelAdmin):
    list_display = ('user', 'domain_for_selector', 'selector_type', 'user_selector')
    list_filter = ('user',)


admin.site.register(models.UserDomainSelectors, UserDomainSelectorsAdmin)
