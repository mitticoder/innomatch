from django.db import models

from shared.models import BaseModel
from users.models import User


class University(BaseModel):
    name = models.CharField(max_length=200, unique=True)
    site = models.CharField(max_length=50)
    hemis_site = models.CharField(max_length=60)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='universities')

    def __str__(self):
        return self.name
