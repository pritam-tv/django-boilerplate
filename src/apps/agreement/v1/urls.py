from django.urls import path
from rest_framework.routers import SimpleRouter

from apps.agreement.v1 import web_views
from apps.agreement.v1.views import (
    AgreementViewSet,
    UserAgreementViewSet,
)

router = SimpleRouter()
router.register(
    "account/agreement",
    AgreementViewSet,
    basename="agreement",
)
router.register(
    "user/me/agreement",
    UserAgreementViewSet,
    basename="user-agreement",
)

urlpatterns = router.urls + [
    path("web/agreement/", web_views.agreement_list, name="web-agreement-list"),
    path(
        "web/agreement/my/",
        web_views.my_agreements,
        name="web-my-agreements",
    ),
]
