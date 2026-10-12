import os
import logging

from django.conf import settings
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail

from .models import Article

logger = logging.getLogger(__name__)


def article_list(request):
    articles = Article.objects.all().order_by("-created_at")

    return render(
        request,
        "articles/list.html",
        {"articles": articles}
    )


def article_detail(request, article_id):
    article = get_object_or_404(
        Article,
        id=article_id
    )

    return render(
        request,
        "articles/detail.html",
        {"article": article}
    )


@login_required
def article_create(request):

    if request.method == "POST":

        title = request.POST["title"]
        content = request.POST["content"]
        image = request.FILES.get("image")

        Article.objects.create(
            author=request.user,
            title=title,
            content=content,
            image=image
        )

        return redirect("/")

    return render(
        request,
        "articles/form.html"
    )


@login_required
def article_edit(request, article_id):

    article = get_object_or_404(
        Article,
        id=article_id
    )

    if article.author != request.user:
        return redirect("/")

    if request.method == "POST":

        article.title = request.POST["title"]
        article.content = request.POST["content"]

        image = request.FILES.get("image")

        if image:
            article.image = image

        article.save()

        return redirect(
            f"/articles/{article.id}/"
        )

    return render(
        request,
        "articles/form.html",
        {"article": article}
    )


@login_required
def article_delete(request, article_id):

    article = get_object_or_404(
        Article,
        id=article_id
    )

    if article.author != request.user:
        return redirect("/")

    if request.method == "POST":

        article.delete()

        return redirect("/")

    return render(
        request,
        "articles/delete.html",
        {"article": article}
    )




def register(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        # 入力チェック
        if not username:
            return render(
                request,
                "articles/register.html",
                {"error": "ユーザー名を入力してください。"}
            )

        if not email:
            return render(
                request,
                "articles/register.html",
                {"error": "メールアドレスを入力してください。"}
            )

        if not password:
            return render(
                request,
                "articles/register.html",
                {"error": "パスワードを入力してください。"}
            )

        # ユーザー名の重複チェック
        if User.objects.filter(username=username).exists():
            return render(
                request,
                "articles/register.html",
                {"error": "このユーザー名はすでに使用されています。"}
            )

        # メールアドレスの重複チェック
        if User.objects.filter(email__iexact=email).exists():
            return render(
                request,
                "articles/register.html",
                {"error": "このメールアドレスはすでに登録されています。"}
            )

        # パスワードの強度チェック
        new_user = User(username=username, email=email)

        try:
            validate_password(password, user=new_user)
        except ValidationError as e:
            return render(
                request,
                "articles/register.html",
                {"error": e.messages}
            )

        # ユーザー登録
        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # 登録完了メールの送信
        try:
            send_mail(
                subject="ご登録ありがとうございます",
                message=(
                    f"{username} 様\n\n"
                    "ご登録ありがとうございます。\n"
                    "会員登録が正常に完了しました。\n\n"
                    "今後ともよろしくお願いいたします。"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

        except Exception:
            # メール送信エラーをRenderのログに記録
            logger.exception("登録完了メールの送信に失敗しました")

        # ログイン画面へ移動
        return redirect("/login/")

    return render(
        request,
        "articles/register.html"
    )




def login_view(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("/")

    return render(
        request,
        "articles/login.html"
    )


def logout_view(request):

    logout(request)

    return redirect("/")




def user_list(request):
    if request.method == "POST":
        if request.POST.get("action") == "logout":
            request.session.pop("can_view_user_list", None)
            return redirect("/private-users/")

        password = request.POST.get("password", "")
        expected_password = os.environ.get(
            "DJANGO_USER_LIST_PASSWORD", ""
        )

        if expected_password and password == expected_password:
            request.session["can_view_user_list"] = True
            users = User.objects.all().order_by("-date_joined")
            return render(
                request,
                "articles/user_list.html",
                {"users": users}
            )

        return render(
            request,
            "articles/user_list_password.html",
            {"error": "パスワードが違います。"}
        )

    if request.session.get("can_view_user_list"):
        users = User.objects.all().order_by("-date_joined")
        return render(
            request,
            "articles/user_list.html",
            {"users": users}
        )

    return render(
        request,
        "articles/user_list_password.html",
        {"error": ""}
    )
