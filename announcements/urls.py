from django.urls import path
from announcements.views import AnnouncementListView, AnnouncementCreateView, AnnouncementDetailView, \
    AnnouncementEditView, AnnouncementJoinView

urlpatterns = [
    path('all/', AnnouncementListView.as_view()),
    path('create/', AnnouncementCreateView.as_view()),
    path('<uuid:pk>/', AnnouncementDetailView.as_view()),
    path('<uuid:pk>/editordelete/', AnnouncementEditView.as_view()),
    path('<uuid:pk>/join/', AnnouncementJoinView.as_view()),
]
