from django.urls import path
from rest_framework.routers import DefaultRouter

from universities.views import UniversityViewSet, UniversityRetrieveView

router = DefaultRouter()
router.register(r'', UniversityViewSet, basename='univercity')
urlpatterns = router.urls

urlpatterns += [
    path('my/', UniversityRetrieveView.as_view())
]
