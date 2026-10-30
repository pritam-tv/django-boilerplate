import uuid as uuid_module

from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.cms.models import Event, Faq, FaqCategory, Notice


@require_http_methods(["GET"])
def notice_list(request):
    """웹 공지사항 목록"""
    now = timezone.now()
    notices = Notice.objects.filter(
        is_published=True,
        start_at__lte=now,
    ).filter(Q(end_at__gte=now) | Q(end_at__isnull=True))
    query = request.GET.get("q", "").strip()
    if query:
        notices = notices.filter(title__icontains=query)
    notices = notices.order_by("-published_at")
    return render(
        request,
        "web/cms/notice_list.html",
        {"notices": notices, "query": query},
    )


@require_http_methods(["GET"])
def notice_detail(request, uuid):
    """웹 공지사항 상세"""
    now = timezone.now()
    notice = get_object_or_404(
        Notice,
        uuid=uuid,
        is_published=True,
        start_at__lte=now,
    )
    if notice.end_at and notice.end_at < now:
        raise Http404("공지사항을 찾을 수 없습니다.")
    return render(request, "web/cms/notice_detail.html", {"notice": notice})


@require_http_methods(["GET"])
def event_list(request):
    """웹 이벤트 목록"""
    now = timezone.now()
    events = Event.objects.filter(
        is_published=True,
        start_at__lte=now,
    ).filter(Q(end_at__gte=now) | Q(end_at__isnull=True))
    query = request.GET.get("q", "").strip()
    if query:
        events = events.filter(title__icontains=query)
    events = events.order_by("-published_at")
    return render(
        request,
        "web/cms/event_list.html",
        {"events": events, "query": query},
    )


@require_http_methods(["GET"])
def event_detail(request, uuid):
    """웹 이벤트 상세"""
    now = timezone.now()
    event = get_object_or_404(
        Event,
        uuid=uuid,
        is_published=True,
        start_at__lte=now,
    )
    if event.end_at and event.end_at < now:
        raise Http404("이벤트를 찾을 수 없습니다.")
    is_event_ended = bool(event.event_end_at and event.event_end_at <= now)
    return render(
        request,
        "web/cms/event_detail.html",
        {"event": event, "is_event_ended": is_event_ended},
    )


@require_http_methods(["GET"])
def faq_list(request):
    """웹 FAQ 목록"""
    faqs = Faq.objects.filter(is_published=True).select_related("category")
    categories = FaqCategory.objects.all().order_by("name")
    category_uuid = request.GET.get("category", "").strip()
    if category_uuid:
        try:
            uuid_module.UUID(category_uuid)
        except ValueError:
            category_uuid = ""
        else:
            faqs = faqs.filter(category__uuid=category_uuid)
    faqs = faqs.order_by("category__name", "-published_at")
    return render(
        request,
        "web/cms/faq_list.html",
        {
            "faqs": faqs,
            "categories": categories,
            "category_uuid": category_uuid,
        },
    )
