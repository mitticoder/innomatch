from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from announcements.models import Announcement, Participant


class AnnouncementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['title', 'text', 'image', 'video', 'expiration_date']

    def validate(self, data):
        super(AnnouncementCreateSerializer, self).validate(data)


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'text', 'image', 'video', 'expiration_date', 'university']


class ParticipantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = []

    def validate(self, data):
        announcement_id = self.context['view'].kwargs.get('pk')

        try:
            announcement = Announcement.objects.get(id=announcement_id)
        except Announcement.DoesNotExist:
            raise serializers.ValidationError(
                {'success': False, 'message': 'E\'lon topilmadi!'}
            )

        if announcement.is_expired():
            raise serializers.ValidationError(
                {'success': False, 'message': 'E\'lon vaqti tugagan!'}
            )

        user = self.context['request'].user
        if Participant.objects.filter(announcement__id=announcement.id, user=user).exists():
            raise serializers.ValidationError(
                {'success': False, 'message': 'Siz allaqachon ushbu e\'longa qo\'shilgansiz!'}
            )

        return data

    def to_representation(self, instance):
        data = super(ParticipantCreateSerializer, self).to_representation(instance)
        data.update(
            {
                'success': True,
                'message': 'Siz bu bellashuvga qo\'shildingiz!',
            }
        )
        return data

