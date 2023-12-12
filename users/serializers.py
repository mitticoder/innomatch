from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken

from shared.utility import send_phone_code, get_data
from users.models import User, VIA_PHONE, NEW, CODE_VERIFIED, DONE


class LoginSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.fields['password'] = serializers.CharField(required=True)

    def auth_validate(self, data):
        username = data.get('username')
        password = data.get('password')
        if not str(username).startswith('+998') and not User.objects.filter(username=username).exists():
            data = get_data(username, password)
            user = User.objects.create(**data)
            user.set_password(password)
            user.save()
        user = self.get_user(username=username)
        if user is not None and user.auth_status == NEW:
            raise ValidationError(
                {
                    'success': False,
                    'message': "Siz Shaxsingizni tasdiqlamagansiz!"
                }
            )
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            self.user = user
        else:
            raise ValidationError(
                {
                    'success': False,
                    'message': "Kechirasiz, siz kiritgan login yoki parol noto'g'ri. Tekshirib, qayta urinib koʻring!"
                }
            )

    def validate(self, data):
        self.auth_validate(data)
        if self.user.auth_status == NEW:
            raise PermissionDenied("Siz login qila olmaysiz. Ruxsatingiz yo'q!")
        data = {
            'success': True,
            'message': 'Tizimga muvofaqiyatli kirdingiz!',
            'data': self.user.token()
        }
        return data

    def get_user(self, **kwargs):
        users = User.objects.filter(**kwargs)
        if not users.exists():
            raise ValidationError(
                {
                    'success': False,
                    "message": "Faol foydalanuvchi topilmadi!"
                }
            )
        return users.first()


class LoginRefreshSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        access_token_instance = AccessToken(data['access'])
        user_id = access_token_instance['user_id']
        user = get_object_or_404(User, id=user_id)
        update_last_login(None, user)
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        phone = attrs.get('phone', None)
        if phone is None:
            raise ValidationError(
                {
                    "success": False,
                    'message': "Telefon raqami kiritilishi shart!"
                }
            )
        user = User.objects.filter(phone_number=phone)
        if not user.exists():
            raise NotFound(detail="Foydalanuvchi topilmadi!")
        attrs['user'] = user.first()
        return attrs


class ResetPasswordSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    password = serializers.CharField(min_length=8, required=True, write_only=True)
    confirm_password = serializers.CharField(min_length=8, required=True, write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'password',
            'confirm_password'
        )

    def validate(self, data):
        password = data.get('password', None)
        confirm_password = data.get('password', None)
        if password != confirm_password:
            raise ValidationError(
                {
                    'success': False,
                    'message': "Parollaringiz qiymati bir-biriga teng emas"
                }
            )
        if password:
            validate_password(password)
        return data

    def update(self, instance, validated_data):
        password = validated_data.pop('password')
        instance.set_password(password)
        return super(ResetPasswordSerializer, self).update(instance, validated_data)


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['confirm_password'] = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'id',
            'auth_type',
            'auth_status',
            'first_name',
            'last_name',
            'phone_number',
            'password',
        )
        extra_kwargs = {
            'auth_type': {'read_only': True, 'required': False},
            'auth_status': {'read_only': True, 'required': False},
            'phone_number': {'required': True}
        }

    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)
        if user.auth_type == VIA_PHONE:
            code = user.create_verify_code()
            send_phone_code(user.phone_number, code)
        user.save()
        return user

    def validate(self, data):
        super(SignUpSerializer, self).validate(data)
        data = self.auth_validate(data)
        return data

    @staticmethod
    def auth_validate(data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        if password != confirm_password:
            raise serializers.ValidationError({'success': False, 'message': 'Parollar mos emas!'})

        phone_number = '+' + ''.join(filter(str.isdigit, str(data.get('phone_number'))))
        if phone_number != '+':
            data = {
                'username': phone_number,
                "phone_number": phone_number,
                "auth_type": VIA_PHONE
            }
        else:
            data = {
                'success': False,
                'message': "Hemis va parol yoki telefon raqam kiritishingiz kerak!"
            }
            raise ValidationError(data)
        print(data)

        return data

    def validate_phone_number(self, value):
        value = value.lower()
        if value and User.objects.filter(phone_number=value).exists():
            data = {
                "success": False,
                "message": "Bu telefon raqami allaqachon ma'lumotlar bazasida bor!"
            }
            raise ValidationError(data)

        return value

    def to_representation(self, user):
        data = super(SignUpSerializer, self).to_representation(user)
        data.update(user.token())
        return data


class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'email', 'username', 'hemis', 'image']
