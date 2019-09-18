from rest_framework import serializers

from Notice.models import Notice


class NoticeSerializers(serializers.ModelSerializer):
    class Meta:
        model = Notice
        read_only_fields = ('user',)
        fields = "__all__"


class PublicNoticeSerializers(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = "__all__"
