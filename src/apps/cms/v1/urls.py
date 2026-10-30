from django.urls import path
from rest_framework.routers import SimpleRouter

from apps.cms.v1 import web_views
from apps.cms.v1.views import NoticeViewSet, EventViewSet, FaqViewSet

router = SimpleRouter()
router.register("cms/notice", NoticeViewSet, basename="cms-notice")
router.register("cms/event", EventViewSet, basename="cms-event")
router.register("cms/faq", FaqViewSet, basename="cms-faq")

urlpatterns = router.urls + [
    path("web/cms/notice/", web_views.notice_list, name="web-cms-notice-list"),
    path(
        "web/cms/notice/<uuid:uuid>/",
        web_views.notice_detail,
        name="web-cms-notice-detail",
    ),
    path("web/cms/event/", web_views.event_list, name="web-cms-event-list"),
    path(
        "web/cms/event/<uuid:uuid>/",
        web_views.event_detail,
        name="web-cms-event-detail",
    ),
    path("web/cms/faq/", web_views.faq_list, name="web-cms-faq-list"),
]
