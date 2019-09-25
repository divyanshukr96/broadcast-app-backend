from rest_framework import serializers

from Files.models import Files


class FileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Files
        fields = ('id', 'file',)
