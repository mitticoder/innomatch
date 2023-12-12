from django.urls import path
from users.views import CreateUserView, LoginView, LogOutView, LoginRefreshView, VerifyAPIView, GetNewVerification, \
    ForgotPasswordView, ResetPasswordView, UserRetrieveView

urlpatterns = [
    path('me/', UserRetrieveView.as_view()),
    path('login/', LoginView.as_view()),
    path('login/refresh/', LoginRefreshView.as_view()),
    path('logout/', LogOutView.as_view()),
    path('signup/', CreateUserView.as_view()),
    path('verify/', VerifyAPIView.as_view()),
    path('new-verify/', GetNewVerification.as_view()),
    # path('forgot-password/', ForgotPasswordView.as_view()),
    # path('reset-password/', ResetPasswordView.as_view()),
]
