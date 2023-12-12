import requests
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from rest_framework.exceptions import ValidationError

from universities.models import University
from users.models import VIA_HEMIS, DONE


def save_image_to_media(image_url, hemis):
    response = requests.get(image_url)
    if response.status_code == 200:
        image_content = ContentFile(response.content)
        image_name = f"{hemis}.jpg"
        image = ImageFile(image_content, name=image_name)
        return image
    return None


def send_phone_code(phone, code):
    print(code)


def get_data(hemis, password):
    universities = University.objects.all()

    for i in universities:
        response = requests.post(
            url=i.hemis_site + 'rest/v1/auth/login',
            data={
                "login": hemis,
                "password": password,
            })
        if response.ok:
            data = response.json()
            if data['success']:
                response = requests.get(
                    url=i.hemis_site + 'rest/v1/account/me',
                    headers={
                        "Authorization": f"Bearer {data['data']['token']}",
                    })
                data = response.json()['data']
                image_url = data['image']
                image = save_image_to_media(image_url, hemis)
                return {
                    'username': hemis,
                    'hemis': hemis,
                    'auth_type': VIA_HEMIS,
                    'auth_status': DONE,
                    'university': i,
                    'first_name': data['first_name'],
                    'last_name': data['second_name'],
                    'email': data['email'],
                    'phone_number': data['phone'],
                    'image': image,
                }

    raise ValidationError(
        {
            'success': False,
            'message': 'Hemis login yoki parol xato!'
        }
    )
