import os
import secrets
import resend
from django.http import HttpResponse
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
from django.views.decorators.http import require_http_methods

from .models import Article

logger = logging.getLogger(__name__)


def article_list(request):
    articles = Article.objects.all().order_by("-created_at")

    return render(
        request,
        "articles/index.html",
        {"articles": articles}
    )


def category_list(request, category_slug):
    category_names = {
        "music": "音楽",
        "movie": "映画",
        "book": "読書",
        "photo": "写真",
        "travel": "旅行",
        "cooking": "料理",
        "other": "その他",
    }

    category_name = category_names.get(category_slug)

    if category_name is None:
        return HttpResponse("カテゴリーが見つかりません。", status=404)

    articles = Article.objects.filter(
        category=category_slug
    ).order_by("-created_at")

    return render(
        request,
        "articles/category.html",
        {
            "articles": articles,
            "category_name": category_name,
            "category_slug": category_slug,
        }
    )

def genre_list(request, genre_slug):
    genre_names = {
        "hobby": "趣味・エンタメ",
        "people": "人・社会",
        "life": "暮らし",
        "learning": "学び・仕事",
        "creative": "創作・表現",
        "other": "その他",
    }

    genre_name = genre_names.get(genre_slug)

    if genre_name is None:
        return HttpResponse("ジャンルが見つかりません。", status=404)

    articles = Article.objects.filter(
        genre=genre_slug
    ).order_by("-created_at")

    return render(
        request,
        "articles/genre.html",
        {
            "articles": articles,
            "genre_name": genre_name,
            "genre_slug": genre_slug,
        }
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
        genre = request.POST.get("genre", "other")
        category = request.POST.get("category", "other")
        image = request.FILES.get("image")
        youtube_url = request.POST.get("youtube_url", "").strip()

        valid_categories = [
            "music",
            "movie",
            "book",
            "photo",
            "travel",
            "cooking",
            "other",
        ]

        if category not in valid_categories:
            category = "other"

        Article.objects.create(
            author=request.user,
            title=title,
            content=content,
            genre=genre,
            category=category,
            image=image,
            youtube_url=youtube_url
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

        category = request.POST.get(
            "category",
            article.category
        )

        valid_categories = [
            "music",
            "movie",
            "book",
            "photo",
            "travel",
            "cooking",
            "other",
        ]

        valid_genres = [
            "hobby",
            "people",
            "life",
            "learning",
            "creative",
            "other",
        ]

        if genre not in valid_genres:
            genre = "other"

        if category in valid_categories:
            article.category = category

        youtube_url = request.POST.get(
            "youtube_url",
            article.youtube_url
        ).strip()

        article.youtube_url = youtube_url

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

        # Resendを使って登録完了メールを送信
        try:
            resend.api_key = os.environ["RESEND_API_KEY"]

            resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": [email],
                "subject": "ご登録ありがとうございます",
                "text": (
                    f"{username} 様\n\n"
                    "ご登録ありがとうございます。\n"
                    "会員登録が正常に完了しました。\n\n"
                    "今後ともよろしくお願いいたします。"
                ),
            })

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

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("/")

        # ログイン失敗時のメッセージ
        if not User.objects.filter(username=username).exists():
            error = "ユーザー名が間違っています。"
        else:
            error = "パスワードが間違っています。"

        return render(
            request,
            "articles/login.html",
            {"error": error}
        )

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

# プライバシーポリシー
def privacy(request):
    return render(request, "articles/privacy.html")


# 利用規約
def terms(request):
    return render(request, "articles/terms.html")


# このサイトについて
def about(request):
    return render(request, "articles/about.html")


# お問い合わせ
def contact(request):
    return render(request, "articles/contact.html")


# ご利用ガイド
def guide(request):
    return render(request, "articles/guide.html")




