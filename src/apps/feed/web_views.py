from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.html import escape
from django.views.decorators.http import require_http_methods, require_POST

from apps.feed.models import (
    Feed,
    FeedComment,
    FeedLike,
    FeedTag,
)

LOGIN_URL = "/v1/web/account/login/"


def _parse_tags(raw_tags):
    """쉼표로 구분된 태그 문자열을 태그 목록으로 변환"""
    names = [name.strip() for name in raw_tags.split(",") if name.strip()]
    return list(dict.fromkeys(names))[:10]


def _published_feeds():
    """공개된 피드 목록 조회"""
    return (
        Feed.objects.filter(
            is_deleted=False,
            is_displayed=True,
            published_at__lte=timezone.now(),
        )
        .select_related("user__profile")
        .prefetch_related("tags")
        .order_by("-published_at")
    )


@require_http_methods(["GET"])
def feed_list(request):
    """웹 피드 목록 페이지"""
    feeds = _published_feeds()
    tag_name = request.GET.get("tag", "").strip()
    if tag_name:
        feeds = feeds.filter(tags__name=tag_name).distinct()
    return render(
        request,
        "web/feed/list.html",
        {"feeds": feeds, "tag_name": tag_name},
    )


@require_http_methods(["GET"])
def feed_detail(request, uuid):
    """웹 피드 상세 페이지"""
    feed = get_object_or_404(
        Feed.objects.select_related("user__profile").prefetch_related("tags"),
        uuid=uuid,
        is_deleted=False,
        is_displayed=True,
        published_at__lte=timezone.now(),
    )
    replies = (
        FeedComment.objects.filter(is_displayed=True, is_deleted=False)
        .select_related("user__profile")
        .order_by("created_at")
    )
    comments = (
        FeedComment.objects.filter(
            feed=feed,
            is_displayed=True,
            is_deleted=False,
            parent=None,
        )
        .select_related("user__profile")
        .prefetch_related(Prefetch("replies", queryset=replies))
        .order_by("created_at")
    )
    is_liked = False
    if request.user.is_authenticated:
        is_liked = FeedLike.objects.filter(feed=feed, user=request.user).exists()
    return render(
        request,
        "web/feed/detail.html",
        {"feed": feed, "comments": comments, "is_liked": is_liked},
    )


@require_http_methods(["GET", "POST"])
@login_required(login_url=LOGIN_URL)
def feed_create(request):
    """웹 피드 작성 페이지"""
    if request.method == "POST":
        title = escape(request.POST.get("title", "").strip(), quote=False)
        content = escape(request.POST.get("content", "").strip(), quote=False)
        image = request.POST.get("image", "").strip()
        tag_names = _parse_tags(request.POST.get("tags", ""))

        if not title:
            messages.error(request, "제목을 입력해주세요.")
        elif not content:
            messages.error(request, "내용을 입력해주세요.")
        else:
            with transaction.atomic():
                feed = Feed.objects.create(
                    user=request.user,
                    title=title,
                    content=content,
                    image=image or None,
                    published_at=timezone.now(),
                )
                for name in tag_names:
                    tag, _ = FeedTag.objects.get_or_create(name=name)
                    feed.tags.add(tag)
            messages.success(request, "피드가 등록되었습니다.")
            return redirect("web-feed-detail", uuid=feed.uuid)

    return render(request, "web/feed/form.html")


@require_POST
@login_required(login_url=LOGIN_URL)
def feed_delete(request, uuid):
    """웹 피드 삭제"""
    feed = get_object_or_404(Feed, uuid=uuid, user=request.user, is_deleted=False)
    feed.is_deleted = True
    feed.save(update_fields=["is_deleted", "updated_at"])
    messages.success(request, "피드가 삭제되었습니다.")
    return redirect("web-feed-list")


@require_POST
@login_required(login_url=LOGIN_URL)
def feed_like(request, uuid):
    """웹 피드 좋아요 토글"""
    feed = get_object_or_404(Feed, uuid=uuid, is_deleted=False)
    with transaction.atomic():
        like = FeedLike.objects.filter(feed=feed, user=request.user).first()
        if like:
            like.delete()
            feed.likes_count = max(feed.likes_count - 1, 0)
        else:
            FeedLike.objects.create(feed=feed, user=request.user)
            feed.likes_count += 1
        feed.save(update_fields=["likes_count", "updated_at"])
    return redirect("web-feed-detail", uuid=feed.uuid)


@require_POST
@login_required(login_url=LOGIN_URL)
def feed_comment_create(request, uuid):
    """웹 피드 댓글 작성"""
    feed = get_object_or_404(Feed, uuid=uuid, is_deleted=False)
    content = escape(request.POST.get("content", "").strip(), quote=False)
    if not content:
        messages.error(request, "댓글 내용을 입력해주세요.")
        return redirect("web-feed-detail", uuid=feed.uuid)

    with transaction.atomic():
        FeedComment.objects.create(
            feed=feed,
            user=request.user,
            content=content,
        )
        feed.comments_count += 1
        feed.save(update_fields=["comments_count", "updated_at"])
    return redirect("web-feed-detail", uuid=feed.uuid)
