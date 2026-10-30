from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.account.v1.serializers import (
    EmailVerificationSerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer,
    RegisterSerializer,
)

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


@require_http_methods(["GET", "POST"])
def login_view(request):
    """웹 로그인 페이지"""
    if request.user.is_authenticated:
        return redirect("web-feed-list")

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=email, password=password)
        if user is None:
            messages.error(request, "이메일 또는 비밀번호가 올바르지 않습니다.")
        elif not user.is_verified:
            messages.error(request, "이메일 인증이 완료되지 않았습니다.")
        else:
            login(request, user)
            next_url = request.GET.get("next", "")
            if not next_url.startswith("/"):
                next_url = ""
            return redirect(next_url or "web-feed-list")

    return render(request, "web/account/login.html")


@require_http_methods(["GET", "POST"])
def register_view(request):
    """웹 회원 가입 페이지"""
    if request.method == "POST":
        serializer = RegisterSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            messages.success(
                request, "회원 가입 신청이 완료되었습니다. 이메일 인증 후 로그인해주세요."
            )
            return redirect("web-account-login")
        for error in _serializer_errors(serializer.errors):
            messages.error(request, error)

    return render(request, "web/account/register.html")


def logout_view(request):
    """웹 로그아웃"""
    if request.method == "POST":
        logout(request)
    return redirect("web-account-login")


def confirm_view(request):
    """이메일 인증 처리"""
    serializer = EmailVerificationSerializer(data=request.GET)
    if serializer.is_valid():
        serializer.save()
        messages.success(request, "이메일 인증이 완료되었습니다. 로그인해주세요.")
        return redirect("web-account-login")
    for error in _serializer_errors(serializer.errors):
        messages.error(request, error)
    return render(request, "web/account/confirm_failed.html")


@require_http_methods(["GET", "POST"])
def password_reset_view(request):
    """비밀번호 재설정 요청 페이지"""
    if request.method == "POST":
        serializer = PasswordResetSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.to_representation(None)
            messages.success(request, "비밀번호 재설정 링크를 이메일로 발송했습니다.")
            return redirect("web-account-login")
        for error in _serializer_errors(serializer.errors):
            messages.error(request, error)

    return render(request, "web/account/password_reset.html")


@require_http_methods(["GET", "POST"])
def password_change_view(request):
    """비밀번호 변경 페이지"""
    if request.method == "POST":
        serializer = PasswordChangeSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, "비밀번호가 변경되었습니다. 다시 로그인해주세요.")
            return redirect("web-account-login")
        for error in _serializer_errors(serializer.errors):
            messages.error(request, error)

    return render(
        request,
        "web/account/password_change.html",
        {
            "hashed_email": request.GET.get("hashed_email", ""),
            "token": request.GET.get("token", ""),
        },
    )
