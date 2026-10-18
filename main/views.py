import os
import secrets
import resend
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import F
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


from .models import Article, Profile, Comment

from django.core.paginator import Paginator

logger = logging.getLogger(__name__)



@require_POST
def article_like(request, article_id):
    article = get_object_or_404(
        Article,
        id=article_id
    )

    # Cookieに保存する、この記事専用の識別キー
    cookie_name = f"liked_article_{article.id}"

    # すでにいいね済みなら、件数を増やさない
    if request.COOKIES.get(cookie_name) == "1":
        return JsonResponse({
            "success": True,
            "liked": True,
            "like_count": article.like_count,
        })

    # データベース側で安全に1増やす
    Article.objects.filter(
        id=article.id
    ).update(
        like_count=F("like_count") + 1
    )

    article.refresh_from_db()

    response = JsonResponse({
        "success": True,
        "liked": True,
        "like_count": article.like_count,
    })

    # Cookieを約1年間保存
    response.set_cookie(
        cookie_name,
        "1",
        max_age=60 * 60 * 24 * 365,
        secure=not settings.DEBUG,
        httponly=True,
        samesite="Lax",
    )

    return response



def article_list(request):
    articles = Article.objects.all().order_by("-created_at")

    paginator = Paginator(articles, 12)
    page_obj = paginator.get_page(
        request.GET.get("page", 1)
    )

    context = {
        "articles": page_obj.object_list,
        "page_obj": page_obj,
        "has_next": page_obj.has_next(),
    }

    if request.GET.get("partial") == "1":
        return render(
            request,
            "articles/_article_cards.html",
            context
        )

    return render(
        request,
        "articles/index.html",
        context
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
        return HttpResponse(
            "カテゴリーが見つかりません。",
            status=404
        )

    articles = Article.objects.filter(
        category=category_slug
    ).order_by("-created_at")

    paginator = Paginator(articles, 12)
    page_obj = paginator.get_page(
        request.GET.get("page", 1)
    )

    context = {
        "articles": page_obj.object_list,
        "page_obj": page_obj,
        "category_name": category_name,
        "category_slug": category_slug,
    }

    if request.GET.get("partial") == "1":
        return render(
            request,
            "articles/_category_article_cards.html",
            context
        )

    return render(
        request,
        "articles/category.html",
        context
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

    paginator = Paginator(articles, 12)
    page_obj = paginator.get_page(
        request.GET.get("page", 1)
    )

    context = {
        "articles": page_obj.object_list,
        "page_obj": page_obj,
        "genre_name": genre_name,
        "genre_slug": genre_slug,
    }

    if request.GET.get("partial") == "1":
        return render(
            request,
            "articles/_genre_article_cards.html",
            context
        )

    return render(
        request,
        "articles/genre.html",
        context
    )





def article_detail(request, article_id):
    article = get_object_or_404(
        Article,
        id=article_id
    )

    error = ""

    # コメント投稿処理
    if request.method == "POST":

        name = request.POST.get(
            "name", ""
        ).strip()

        content = request.POST.get(
            "content", ""
        ).strip()

        # 入力チェック
        if not name:
            error = "お名前を入力してください。"

        elif not content:
            error = "コメントを入力してください。"

        elif len(name) > 50:
            error = "お名前は50文字以内で入力してください。"

        elif len(content) > 1000:
            error = "コメントは1000文字以内で入力してください。"

        else:
            # コメントをデータベースに保存
            Comment.objects.create(
                article=article,
                name=name,
                content=content
            )

            # 保存後、記事詳細画面に戻る
            if request.GET.get("from") == "my-articles":
                return redirect(
                    f"/articles/{article.id}/?from=my-articles"
                )

            return redirect(
                f"/articles/{article.id}/"
            )

    # この記事に投稿されたコメントを取得
    comments = Comment.objects.filter(
        article=article
    ).order_by("-created_at")

    return render(
        request,
        "articles/detail.html",
        {
            "article": article,
            "comments": comments,
            "error": error,
            "from_my_articles": (
                request.GET.get("from") == "my-articles"
            ),
        }
    )






@login_required
def article_create(request):

    if request.method == "POST":

        title = request.POST["title"]
        content = request.POST["content"]
        genre = request.POST.get("genre", "other")
        category = request.POST.get("category", "other")

        image = request.FILES.get("image")
        youtube_url = request.POST.get(
            "youtube_url", ""
        ).strip()

        valid_categories = [
            "music", "movie", "book", "photo",
            "travel", "cooking", "other",
        ]

        valid_genres = [
            "hobby", "people", "life",
            "learning", "creative", "other",
        ]

        if category not in valid_categories:
            category = "other"

        if genre not in valid_genres:
            genre = "other"

        article = Article.objects.create(
            author=request.user,
            title=title,
            content=content,
            genre=genre,
            category=category,
            image=image,
            youtube_url=youtube_url,
        )

        return redirect("my_articles")

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

        genre = request.POST.get(
            "genre", article.genre
        )

        valid_genres = [
            "hobby", "people", "life",
            "learning", "creative", "other",
        ]

        if genre in valid_genres:
            article.genre = genre

        category = request.POST.get(
            "category", article.category
        )

        valid_categories = [
            "music", "movie", "book", "photo",
            "travel", "cooking", "other",
        ]

        if category in valid_categories:
            article.category = category

        # YouTube動画は1本
        youtube_url = request.POST.get(
            "youtube_url", article.youtube_url
        ).strip()

        # 新しい画像が選ばれた場合だけ差し替える
        image = request.FILES.get("image")

        if image:
            article.image = image

        article.youtube_url = youtube_url
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
            return redirect("my_articles")

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




def my_articles(request):
    if not request.user.is_authenticated:
        return redirect("/login/")

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    articles = Article.objects.filter(
        author=request.user
    ).order_by("-created_at")

    paginator = Paginator(articles, 12)
    page_obj = paginator.get_page(
        request.GET.get("page", 1)
    )

    context = {
        "articles": page_obj.object_list,
        "page_obj": page_obj,
        "has_next": page_obj.has_next(),
        "profile": profile,
        "page_title": f"{request.user.username}さんの投稿",
    }

    if request.GET.get("partial") == "1":
        return render(
            request,
            "articles/_my_article_cards.html",
            context
        )

    
    return render(
    request,
    "articles/my_articles.html",
    context
      )






@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        profile.introduction = request.POST.get(
            "introduction", ""
        ).strip()

        profile.favorite_things = request.POST.get(
            "favorite_things", ""
        ).strip()

        image = request.FILES.get("image")
        if image:
            profile.image = image

        profile.save()

        return redirect("my_articles")

    return render(
        request,
        "articles/profile_edit.html",
        {"profile": profile}
    )




def public_profile(request, username):
    profile_user = get_object_or_404(
        User,
        username=username
    )

    profile = Profile.objects.filter(
        user=profile_user
    ).first()

    articles = Article.objects.filter(
        author=profile_user
    ).order_by("-created_at")

    paginator = Paginator(articles, 8)

    page_obj = paginator.get_page(
        request.GET.get("page", 1)
    )

    context = {
        "profile_user": profile_user,
        "profile": profile,
        "articles": page_obj.object_list,
        "page_obj": page_obj,
        "has_next": page_obj.has_next(),
    }

    if request.GET.get("partial") == "1":
        return render(
            request,
            "articles/_public_profile_cards.html",
            context
        )

    return render(
        request,
        "articles/public_profile.html",
        context
    )








