from django.shortcuts import render
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from universities.permissions import IsUniversityResponsibleUser
from universities.serializers import UniversitySerializer
from universities.models import University


class UniversityViewSet(ModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = (IsAdminUser, IsUniversityResponsibleUser, )


class UniversityRetrieveView(RetrieveAPIView):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = (IsAuthenticated, )

    def get_object(self):
        return self.request.user.university


