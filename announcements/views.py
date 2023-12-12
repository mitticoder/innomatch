from django.db.models import Q
from rest_framework import permissions, generics, status
from rest_framework.response import Response

from announcements.models import Announcement, Participant
from announcements.serializers import AnnouncementSerializer, AnnouncementCreateSerializer, ParticipantCreateSerializer
from announcements.permissions import IsAnnouncementOwner, CanAddAnnouncement


class AnnouncementListView(generics.ListAPIView):
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        user = self.request.user
        university = user.university
        if user.is_superuser:
            return Announcement.objects.all()
        if university:
            return Announcement.objects.filter(Q(university=university) | Q(university__isnull=True))
        return Announcement.objects.filter(university__isnull=True)


class AnnouncementCreateView(generics.CreateAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementCreateSerializer
    permission_classes = [CanAddAnnouncement]


class AnnouncementDetailView(generics.RetrieveAPIView):
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        user = self.request.user
        university = user.university
        if user.is_superuser:
            return Announcement.objects.all()
        if university:
            return Announcement.objects.filter(Q(university=university) | Q(university__isnull=True))
        return Announcement.objects.filter(university__isnull=True)


class AnnouncementEditView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated, IsAnnouncementOwner]


class AnnouncementJoinView(generics.CreateAPIView):
    queryset = Participant.objects.all()
    serializer_class = ParticipantCreateSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def perform_create(self, serializer):
        announcement_id = self.kwargs['pk']
        announcement = Announcement.objects.get(pk=announcement_id)
        serializer.save(user=self.request.user, announcement=announcement)
