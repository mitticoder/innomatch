import random
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.datetime_safe import datetime
from rest_framework_simplejwt.tokens import RefreshToken
from shared.models import BaseModel

ORDINARY_USER, MANAGER, ADMIN = ("ordinary_user", 'manager', 'admin')
VIA_HEMIS, VIA_PHONE = ("via_hemis", "via_phone")
NEW, CODE_VERIFIED, DONE = ('new', 'code_verified', 'done')


class User(AbstractUser):
    USER_ROLES = (
        (ORDINARY_USER, ORDINARY_USER),
        (MANAGER, MANAGER),
        (ADMIN, ADMIN)
    )
    AUTH_TYPE_CHOICES = (
        (VIA_PHONE, VIA_PHONE),
        (VIA_HEMIS, VIA_HEMIS)
    )
    AUTH_STATUS = (
        (NEW, NEW),
        (CODE_VERIFIED, CODE_VERIFIED),
        (DONE, DONE)
    )

    id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, primary_key=True)
    user_role = models.CharField(max_length=31, choices=USER_ROLES, default=ORDINARY_USER)
    auth_status = models.CharField(max_length=31, choices=AUTH_STATUS, default=NEW)
    auth_type = models.CharField(max_length=31, choices=AUTH_TYPE_CHOICES, default=VIA_HEMIS)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    image = models.ImageField(upload_to='profile/', null=True, blank=True)
    hemis = models.CharField(max_length=20, unique=True, null=True, blank=True)
    score_local = models.IntegerField(default=0)
    score_global = models.IntegerField(default=0)
    university = models.ForeignKey('universities.University', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='users')
    REQUIRED_FIELDS = ['phone_number']

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.auth_status = DONE
            self.user_role = ADMIN
            self.auth_type = VIA_PHONE

        super(User, self).save(*args, **kwargs)

    def create_verify_code(self):
        code = "".join([str(random.randint(0, 10000) % 10) for _ in range(4)])
        UserConfirmation.objects.create(
            user_id=self.id,
            code=code
        )
        return code

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            "access": str(refresh.access_token),
            "refresh_token": str(refresh)
        }


PHONE_EXPIRE = 2


class UserConfirmation(BaseModel):
    code = models.CharField(max_length=4)
    user = models.ForeignKey('users.User', models.CASCADE, related_name='verify_codes')
    expiration_time = models.DateTimeField(null=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.__str__())

    def save(self, *args, **kwargs):
        self.expiration_time = datetime.now() + timedelta(minutes=PHONE_EXPIRE)
        super(UserConfirmation, self).save(*args, **kwargs)
