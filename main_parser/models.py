from django.db import models
from django.conf import settings


class UserDomainSelectors(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)

    domain_for_selector = models.CharField(max_length=200, default='')
    selector_type = models.CharField(max_length=200, default='')
    user_selector = models.CharField(max_length=200, default='')

    class Meta:
        verbose_name_plural = 'User selectors'

    def __str__(self):
        return self.selector_type
