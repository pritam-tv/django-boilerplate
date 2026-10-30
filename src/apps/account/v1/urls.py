from django.urls import path
from rest_framework.routers import SimpleRouter

from apps.account.v1 import web_views
from apps.account.v1.views import (
    LoginViewSet,
    RegisterViewSet,
    PasswordViewSet,
    GoogleLoginViewSet,
)

router = SimpleRouter()
router.register("account", LoginViewSet, basename="user")
router.register("account/register", RegisterViewSet, basename="register")
router.register("account/password", PasswordViewSet, basename="password")
router.register("account/google", GoogleLoginViewSet, basename="google_login")

urlpatterns = router.urls + [
    path("web/account/login/", web_views.login_view, name="web-account-login"),
    path("web/account/logout/", web_views.logout_view, name="web-account-logout"),
    path(
        "web/account/register/",
        web_views.register_view,
        name="web-account-register",
    ),
    path("web/account/confirm/", web_views.confirm_view, name="web-account-confirm"),
    path(
        "web/account/password/reset/",
        web_views.password_reset_view,
        name="web-account-password-reset",
    ),
    path(
        "web/account/password/change/",
        web_views.password_change_view,
        name="web-account-password-change",
    ),
]
