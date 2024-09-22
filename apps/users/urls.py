from django.urls import path
from .views import CreateUserView, AuthenticateUserView

urlpatterns = [
    path("auth/signup", CreateUserView.as_view(), name="auth_signup"),
    path("auth/login", AuthenticateUserView.as_view()),
]
