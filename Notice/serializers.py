from rest_framework import serializers

from Notice.models import Notice


class NoticeSerializers(serializers.ModelSerializer):
    class Meta:
        model = Notice
        read_only_fields = ('user',)
        fields = "__all__"


class PublicNoticeSerializers(serializers.ModelSerializer):
    user = serializers.SerializerMethodField('is_named_bar')
    created_at = serializers.DateTimeField(format="%Y-%m-%d %I:%M%p")

    class Meta:
        model = Notice
        fields = ('id', 'title', 'description', 'date', 'time', 'venue', 'user', 'created_at')

    @staticmethod
    def is_named_bar(foo):
        return foo.user.name
