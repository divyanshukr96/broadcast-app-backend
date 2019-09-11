from rest_framework import serializers

from Notice.models import Notice


class NoticeSerializers(serializers.ModelSerializer):
    class Meta:
        model = Notice
        # read_only_fields = ('viewed',)
        fields = "__all__"



