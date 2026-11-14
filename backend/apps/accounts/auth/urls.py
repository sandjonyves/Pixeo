"""Routes d'authentification Pixeo."""

from django.urls import path

from apps.accounts.registration.views import RegisterView

from .views import CSRFView, LoginView, LogoutView, MeView, RefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("csrf/", CSRFView.as_view(), name="auth-csrf"),
]
