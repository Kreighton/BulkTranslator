from rest_framework import serializers

from . import models


class SelectorsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.UserDomainSelectors
        fields = ['user', 'selector_type', 'user_selector']