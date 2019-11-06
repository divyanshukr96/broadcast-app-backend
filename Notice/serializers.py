from datetime import datetime

from django.utils.timezone import now
from rest_framework import serializers

from Notice.models import Notice, Image, Bookmark, NoticeView, Interested, TempImage


class ImageSerializers(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"


class NoticeSerializers(serializers.ModelSerializer):
    images = ImageSerializers(many=True, required=False)
    images_list = serializers.SerializerMethodField('notice_images')

    class Meta:
        model = Notice
        read_only_fields = ('user',)
        fields = (
            'id', 'title', 'description', 'date', 'time', 'venue', 'public_notice', 'department', 'images_list',
            'images', 'is_event', 'visible')

    def __init__(self, *args, **kwargs):
        context = kwargs.get('context', None)
        if context:
            request = kwargs['context']['request']
            if request.method in ["POST"]:
                request.POST._mutable = True
                temp_dept = request.POST.getlist('department[]')
                if temp_dept.__len__() >= 1 and not request.POST.getlist('department'):
                    request.POST.setlist('department', temp_dept)
                    request.data.setlist('department', temp_dept)
                request.POST._mutable = False
        super().__init__(*args, **kwargs)

    def notice_images(self, notice):
        request = self.context.get('request')
        try:
            if not notice.created_at:
                return
        except:
            return
        data = notice.image_set.all()
        if data:
            return list(map(lambda d: {
                'id': d.id,
                'url': request.build_absolute_uri(d.image.url)
            }, data))
        return

    def validate_department(self, department):
        # print(department)
        # print(self.context.get('view').request.POST)
        if not department:
            raise serializers.ValidationError("Target Department field is required.")
        return department

    @staticmethod
    def validate_title(title):
        if title and len(title) < 4:
            raise serializers.ValidationError("Notice title should be more than 5 characters")
        return title

    def validate_description(self, description):
        if not self.context.get('view').request.FILES and not description:
            raise serializers.ValidationError("Notice description / image is required")
        if description and len(description) < 10:
            raise serializers.ValidationError("Notice description should be more than 10 characters")
        return description

    def validate_venue(self, venue):
        is_event = self.initial_data.get('is_event')
        if is_event and not venue:
            raise serializers.ValidationError("Event venue field is required.")
        return venue

    # def validate_time(self, time):
    #     date = self.initial_data.get('date')
    #     if time and not date:
    #         raise serializers.ValidationError("Event date field is required.")
    #     return time

    def validate_date(self, date):
        time = self.initial_data.get('time')
        if time and not date:
            raise serializers.ValidationError("Event date field is required.")
        event_date_time = (str(date) + ' ' + time + ':00') if time else date
        time_format = "%Y-%m-%d %H:%M:%S" if time else "%m/%d/%Y %H:%M:%S"
        event_date_time = datetime.strptime(event_date_time, time_format)
        if datetime.now() >= event_date_time:
            raise serializers.ValidationError("Event date and time is invalid.")

        return date

    def validate_visible(self, visible):
        public_notice = self.initial_data.get('public_notice')

        if public_notice not in ['1', 'true', True, 1]:
            return False

        return visible

    def create(self, validated_data):
        departments = ""
        images_data = self.context.get('view').request.FILES
        try:
            img = validated_data.pop('images')
        except KeyError:
            pass
        try:
            departments = validated_data.pop('department')
        except KeyError:
            pass
        notice = Notice.objects.create(**validated_data)
        if departments:
            notice.department.set(departments)
        for image_data in images_data.values():
            Image.objects.create(notice=notice, image=image_data)
        return notice

    def update(self, instance, validated_data):
        images_data = self.context.get('view').request.FILES

        if len(images_data) > 0:
            temp_img = Image.objects.filter(notice=instance)
            # for img in temp_img:
            #     img.delete()
            for image_data in images_data.values():
                Image.objects.create(notice=instance, image=image_data)

        try:
            img = validated_data.pop('images')
        except KeyError:
            pass

        try:
            departments = validated_data.pop('department')
            if departments:
                instance.department.set(departments)
        except KeyError:
            pass

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)

        instance.is_event = validated_data.get('is_event', instance.is_event)
        instance.venue = validated_data.get('venue', instance.venue)
        instance.date = validated_data.get('date', instance.date)
        instance.time = validated_data.get('time', instance.time)

        instance.public_notice = validated_data.get('public_notice', instance.public_notice)
        instance.visible = validated_data.get('visible', instance.visible)

        instance.save()

        return instance


class PublicNoticeSerializers(serializers.ModelSerializer):
    can_edit = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField('notice_user')
    username = serializers.SerializerMethodField('notice_username')
    images = serializers.SerializerMethodField('notice_images')
    datetime = serializers.SerializerMethodField('notice_created')
    images_list = serializers.SerializerMethodField('notice_images_list')
    profile = serializers.SerializerMethodField('user_profile')
    bookmark = serializers.SerializerMethodField('bookmark_check')
    interested = serializers.SerializerMethodField('interested_check')
    created_at = serializers.DateTimeField(format="%d-%m-%Y, %H:%M")
    time = serializers.TimeField(format="%H:%M")
    date = serializers.TimeField(format="%d-%m-%Y")

    class Meta:
        model = Notice
        fields = (
            'id', 'title', 'description', 'is_event', 'date', 'time', 'venue', 'user', 'username', 'profile', 'images',
            'images_list',
            'department', 'public_notice', 'visible', 'can_edit', 'bookmark', 'interested', 'created_at', 'datetime')

    def get_can_edit(self, notice):
        request = self.context.get('request')
        if notice.user.user_type in ['DEPARTMENT', 'SOCIETY', 'CHANNEL'] and notice.user == request.user:
            return (now() - notice.created_at).days <= 1
        return False

    @staticmethod
    def notice_user(notice):
        return notice.user.name

    @staticmethod
    def notice_username(notice):
        return notice.user.username

    @staticmethod
    def notice_created(notice):
        return notice.created_at

    def user_profile(self, notice):
        request = self.context.get('request')
        if notice.user.profile:
            return request.build_absolute_uri(notice.user.profile.url)

    def notice_images(self, notice):
        request = self.context.get('request')
        data = notice.image_set.all()
        if data:
            return list(map(lambda d: request.build_absolute_uri(d.image.url), data))
        return

    def notice_images_list(self, notice):
        request = self.context.get('request')
        data = notice.image_set.all()
        if data:
            return list(map(lambda d: {
                'id': d.id,
                'url': request.build_absolute_uri(d.image.url)
            }, data))
        return

    def bookmark_check(self, notice):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Bookmark.objects.filter(user=user, notice=notice).exists()
        return False

    def interested_check(self, notice):
        user = self.context.get('request').user
        if user.is_authenticated and notice.is_event:
            return Interested.objects.filter(user=user, notice=notice).exists()
        return False


class NoticeImageSerializers(serializers.ModelSerializer):
    class Meta:
        model = Notice


class NoticeViewsSerializers(serializers.ModelSerializer):
    class Meta:
        model = NoticeView
        fields = "__all__"

    def create(self, validated_data):
        return super().create(validated_data)


class TempImageSerializers(serializers.ModelSerializer):
    class Meta:
        model = TempImage
        fields = "__all__"

    def create(self, validated_data):
        return super().create(validated_data)
