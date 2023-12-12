from django.db import models
from django.utils import timezone

from shared.models import BaseModel
from universities.models import University
from users.models import User


class Announcement(BaseModel):
    title = models.CharField(max_length=200)
    text = models.TextField()
    image = models.ImageField(upload_to='ad_images/', null=True, blank=True)
    video = models.FileField(upload_to='ad_videos/', null=True, blank=True)
    expiration_date = models.DateTimeField()
    university = models.ForeignKey(University, on_delete=models.CASCADE, null=True, blank=True)

    def is_expired(self):
        return self.expiration_date < timezone.now().astimezone(self.expiration_date.tzinfo)


class Participant(BaseModel):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')

