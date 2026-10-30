from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.agreement.models import Agreement, UserAgreement
from apps.agreement.v1.serializers import UserAgreementSerializer

LOGIN_URL = "/v1/web/account/login/"


def _serializer_errors(errors):
    """시리얼라이저 오류 메시지 목록 조회"""
    result = []

    def collect(value):
        if isinstance(value, dict):
            if "message" in value:
                result.append(str(value["message"]))
            else:
                for item in value.values():
                    collect(item)
        elif isinstance(value, (list, tuple)):
            for item in value:
                collect(item)
        else:
            result.append(str(value))

    collect(errors)
    return result


@require_http_methods(["GET"])
def agreement_list(request):
    """웹 약관 목록"""
    agreements = Agreement.objects.filter(is_active=True).order_by("order", "id")
    return render(
        request,
        "web/agreement/list.html",
        {"agreements": agreements},
    )


@require_http_methods(["GET", "POST"])
@login_required(login_url=LOGIN_URL)
def my_agreements(request):
    """웹 내 약관 동의 페이지"""
    agreements = Agreement.objects.filter(is_active=True).order_by("order", "id")

    if request.method == "POST":
        agreement_items = []
        has_error = False
        for agreement in agreements:
            is_agreed = request.POST.get(f"agreement_{agreement.id}") == "on"
            if agreement.is_required and not is_agreed:
                messages.error(
                    request, f"필수 약관에 동의해주세요: {agreement.title}"
                )
                has_error = True
            agreement_items.append((agreement, is_agreed))

        if not has_error:
            with transaction.atomic():
                for agreement, is_agreed in agreement_items:
                    user_agreement = UserAgreement.objects.filter(
                        user=request.user,
                        agreement=agreement,
                    ).first()
                    if user_agreement is None:
                        UserAgreement.objects.create(
                            user=request.user,
                            agreement=agreement,
                            is_agreed=is_agreed,
                        )
                    elif user_agreement.is_agreed != is_agreed:
                        serializer = UserAgreementSerializer(
                            user_agreement,
                            data={"is_agreed": is_agreed},
                            partial=True,
                        )
                        if serializer.is_valid():
                            serializer.save()
                        else:
                            for error in _serializer_errors(serializer.errors):
                                messages.error(request, error)
                            has_error = True
            if not has_error:
                messages.success(request, "약관 동의 정보가 저장되었습니다.")
                return redirect("web-agreement-list")

    user_agreement_map = {
        user_agreement.agreement_id: user_agreement
        for user_agreement in UserAgreement.objects.filter(
            user=request.user,
            agreement__in=agreements,
        )
    }
    agreement_rows = [
        (agreement, user_agreement_map.get(agreement.id))
        for agreement in agreements
    ]
    return render(
        request,
        "web/agreement/my_agreements.html",
        {
            "agreements": agreements,
            "agreement_rows": agreement_rows,
        },
    )
