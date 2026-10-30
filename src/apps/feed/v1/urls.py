from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework_nested import routers

from apps.feed.v1 import web_views
from apps.feed.v1.views import (
    FeedViewSet,
    FeedCommentViewSet,
)

feed_router = routers.SimpleRouter()
feed_router.register("feed", FeedViewSet, basename="feed")

comment_router = routers.NestedSimpleRouter(feed_router, r"feed", lookup="feed")
comment_router.register(r"comment", FeedCommentViewSet, basename="feed-comment")

urlpatterns = [
    path("", include(feed_router.urls)),
    path("", include(comment_router.urls)),
    path(
        "web/",
        RedirectView.as_view(pattern_name="web-feed-list", permanent=False),
        name="web-home",
    ),
    path("web/feed/", web_views.feed_list, name="web-feed-list"),
    path("web/feed/create/", web_views.feed_create, name="web-feed-create"),
    path("web/feed/<uuid:uuid>/", web_views.feed_detail, name="web-feed-detail"),
    path(
        "web/feed/<uuid:uuid>/delete/",
        web_views.feed_delete,
        name="web-feed-delete",
    ),
    path("web/feed/<uuid:uuid>/like/", web_views.feed_like, name="web-feed-like"),
    path(
        "web/feed/<uuid:uuid>/comment/",
        web_views.feed_comment_create,
        name="web-feed-comment-create",
    ),
]
