import os
import secrets
import nh3
import resend
from django.db.models import Q
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
from django.contrib.auth.forms import SetPasswordForm
from django.core.mail import send_mail
from django.views.decorators.http import require_http_methods


from .models import (
    Article,
    ArticleLike,
    ArticleView,
    Profile,
    Comment,
    Follow,
)

from django.core.paginator import Paginator

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode,
)
from django.utils.encoding import force_bytes
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta
from django.db.models import Count, Q




logger = logging.getLogger(__name__)


# 記事本文で使用できるHTMLタグ
ARTICLE_CONTENT_TAGS = {
    "p",
    "br",
    "strong",
    "b",
    "em",
    "i",
    "u",
    "s",
    "h1",
    "h2",
    "h3",
    "ol",
    "ul",
    "li",
    "blockquote",
    "pre",
    "code",
    "a",
}


# 記事本文のHTMLを安全に整える
def sanitize_article_content(content):
    return nh3.clean(
        content,
        tags=ARTICLE_CONTENT_TAGS,
        attributes={
            "a": {"href", "title"},
        },
        strip_comments=True,
        link_rel="noopener noreferrer",
    )



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

    
    # いいねの日時を記録する
    ArticleLike.objects.create(
        article=article
    )

    # 累計いいね数を安全に1増やす
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
    articles = Article.objects.filter(
        is_published=True,
        author__is_active=True
    )

    # 検索キーワードを取得
    keyword = request.GET.get("q", "").strip()

    # タイトルまたは本文を検索
    if keyword:
        articles = articles.filter(
            Q(title__icontains=keyword) |
            Q(content__icontains=keyword)
        )

    articles = articles.order_by("-created_at")

    paginator = Paginator(articles, 12)
    page_obj = paginator.get_page(
        request.GET.get("page", 1)
    )

    context = {
        "articles": page_obj.object_list,
        "page_obj": page_obj,
        "has_next": page_obj.has_next(),
        "keyword": keyword,
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

    # 選択されたサブカテゴリーを取得
    sub_category = request.GET.get(
        "sub_category",
        ""
    ).strip()

    # まずカテゴリー全体の記事を取得
    articles = Article.objects.filter(
    category=category_slug,
    is_published=True,
    author__is_active=True
)

    # サブカテゴリーが選択されている場合は絞り込む
    if sub_category:
        articles = articles.filter(
            sub_category=sub_category
        )

    articles = articles.order_by("-created_at")

    paginator = Paginator(articles, 12)
    page_obj = paginator.get_page(
        request.GET.get("page", 1)
    )

    context = {
        "articles": page_obj.object_list,
        "page_obj": page_obj,
        "category_name": category_name,
        "category_slug": category_slug,
        "sub_category": sub_category,
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
        "life": "生活・暮らし",
        "science": "科学・技術",
        "business": "経済・ビジネス",
        "nature": "自然・環境",
        "creative": "創作・表現",
        "other": "その他",
    }

    genre_name = genre_names.get(genre_slug)

    if genre_name is None:
        return HttpResponse("ジャンルが見つかりません。", status=404)

    articles = Article.objects.filter(
        genre=genre_slug,
        is_published=True,
        author__is_active=True
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
    id=article_id,
    is_published=True,
    author__is_active=True
)

    
    
    # 記事の閲覧日時を記録
    ArticleView.objects.create(
        article=article
    )

    # 累計閲覧数を1増やす
    article.view_count += 1
    article.save(update_fields=["view_count"])



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
                user=request.user if request.user.is_authenticated else None,
                user_was_registered=request.user.is_authenticated,
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
            "article_content": sanitize_article_content(
                article.content
            ),
            "comments": comments,
            "error": error,
            "from_my_articles": (
                request.GET.get("from") == "my-articles"
            ),
            "own_article": (
                request.user.is_authenticated
                and request.user == article.author
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
        sub_category = request.POST.get("sub_category", "").strip()

        image = request.FILES.get("image")
        youtube_url = request.POST.get(
            "youtube_url", ""
        ).strip()

        is_published = (
            request.POST.get("action") != "draft"
        )

        valid_categories = [
            "music", "movie", "book", "photo",
            "travel", "cooking", "other",
        ]

        valid_genres = [
            "hobby", "people", "life", "science",
            "business", "nature", "creative", "other",
        ]

        if category not in valid_categories:
            category = "other"

        if genre not in valid_genres:
            genre = "other"

        Article.objects.create(
            author=request.user,
            title=title,
            content=content,
            genre=genre,
            category=category,
            sub_category=sub_category,
            image=image,
            youtube_url=youtube_url,
            is_published=is_published,
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
        id=article_id,
        author=request.user
    )

    if request.method == "POST":

        article.title = request.POST["title"]
        article.content = sanitize_article_content(
            request.POST.get("content", "")
        )

        genre = request.POST.get(
            "genre", article.genre
        )

        valid_genres = [
            "hobby", "people", "life", "science",
            "business", "nature", "creative", "other",
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

        article.sub_category = request.POST.get(
            "sub_category",
            article.sub_category
        ).strip()

        article.youtube_url = request.POST.get(
            "youtube_url",
            article.youtube_url
        ).strip()

        image = request.FILES.get("image")
        if image:
            article.image = image

        action = request.POST.get("action", "publish")

        if action == "draft":
            article.is_published = False
        else:
            article.is_published = True

        article.save()

        if article.is_published:
            return redirect(
                f"/articles/{article.id}/"
            )

        return redirect("/my-articles/?status=draft")

    return render(
        request,
        "articles/form.html",
        {
            "article": article,
            "hide_discovery_menu": True,
        }
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
        {
            "article": article,
            "hide_discovery_menu": True,
        }
    )




def register(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

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

        if User.objects.filter(username=username).exists():
            return render(
                request,
                "articles/register.html",
                {"error": "このユーザー名はすでに使用されています。"}
            )

        if User.objects.filter(email__iexact=email).exists():
            return render(
                request,
                "articles/register.html",
                {"error": "このメールアドレスはすでに登録されています。"}
            )

        new_user = User(username=username, email=email)

        try:
            validate_password(password, user=new_user)
        except ValidationError as e:
            return render(
                request,
                "articles/register.html",
                {"error": e.messages}
            )

        # 仮登録（メール認証が終わるまでログイン不可）
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=False
        )

        try:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            verify_url = request.build_absolute_uri(
                reverse(
                    "verify_email",
                    kwargs={
                        "uidb64": uid,
                        "token": token,
                    }
                )
            )

            resend.api_key = os.environ["RESEND_API_KEY"]

            sender = os.environ.get(
                "RESEND_FROM_EMAIL",
                "noreply@sukitsuna.com",
            )

            resend.Emails.send({
                "from": sender,
                "to": [email],
                "subject": "すきつな｜メールアドレスの確認",
                "text": (
                    f"{username} 様\n\n"
                    "すきつなへのご登録ありがとうございます。\n\n"
                    "以下のリンクをクリックして、"
                    "メールアドレスの認証を完了してください。\n\n"
                    f"{verify_url}\n\n"
                    "このメールに心当たりがない場合は、"
                    "メールを破棄してください。\n\n"
                    "すきつな運営チーム"
                ),
            })

        except Exception:
            logger.exception("メール認証メールの送信に失敗しました")

            return render(
                request,
                "articles/register.html",
                {"error": "認証メールを送信できませんでした。時間をおいて再度お試しください。"}
            )

        return render(
            request,
            "articles/register.html",
            {
                "message": (
                    "確認メールを送信しました。"
                    "メールに記載されたリンクをクリックして、"
                    "登録を完了してください。"
                )
            }
        )

    return render(
        request,
        "articles/register.html"
    )

def verify_email(request, uidb64, token):

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return HttpResponse("認証リンクが正しくありません。")

    if user.is_active:
        return HttpResponse("このメールアドレスはすでに認証済みです。")

    if default_token_generator.check_token(user, token):

        user.is_active = True
        user.save()

        try:
            resend.api_key = os.environ["RESEND_API_KEY"]

            sender = os.environ.get(
                "RESEND_FROM_EMAIL",
                "noreply@sukitsuna.com",
            )

            resend.Emails.send({
                "from": sender,
                "to": [user.email],
                "subject": "すきつなへのご登録ありがとうございます",
                "text": (
                    f"{user.username} 様\n\n"
                    "すきつなへのご登録ありがとうございます。\n\n"
                    "すきつなは、「好きでつながる。世界が広がる。」をテーマにしたコミュニティサイトです。\n\n"
                    "あなたの好きなことを投稿したり、ほかのユーザーの投稿を読んだりしながら、新しいつながりを見つけてみてください。\n\n"
                    "これから、すきつなをどうぞよろしくお願いいたします。\n\n"
                    "すきつな運営チーム"
                ),
            })

        except Exception:
            logger.exception("登録完了メールの送信に失敗しました")

        return render(
            request,
            "articles/email_verified.html"
        )

    return HttpResponse(
        "認証リンクの有効期限が切れているか、無効です。"
    )

def resend_verification(request):

    message = ""

    if request.method == "POST":

        email = request.POST.get("email", "").strip()

        user = User.objects.filter(
            email__iexact=email,
            is_active=False
        ).first()

        if user:

            try:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                verify_url = request.build_absolute_uri(
                    reverse(
                        "verify_email",
                        kwargs={
                            "uidb64": uid,
                            "token": token,
                        }
                    )
                )

                resend.api_key = os.environ["RESEND_API_KEY"]

                sender = os.environ.get(
                    "RESEND_FROM_EMAIL",
                    "noreply@sukitsuna.com",
                )

                resend.Emails.send({
                    "from": sender,
                    "to": [user.email],
                    "subject": "すきつな｜メールアドレスの確認",
                    "text": (
                        f"{user.username} 様\n\n"
                        "すきつなへのご登録ありがとうございます。\n\n"
                        "以下のリンクをクリックして、"
                        "メールアドレスの認証を完了してください。\n\n"
                        f"{verify_url}\n\n"
                        "すきつな運営チーム"
                    ),
                })

            except Exception:
                logger.exception("認証メールの再送に失敗しました")

        message = (
            "該当するアカウントがある場合は、"
            "認証メールを送信しました。メールをご確認ください。"
        )

    return render(
        request,
        "articles/resend_verification.html",
        {"message": message}
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
        existing_user = User.objects.filter(
            username=username
        ).first()

        if existing_user and not existing_user.is_active:
            error = "メールアドレスの認証が完了していません。認証メールをご確認ください。"

        elif existing_user is None:
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
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        if not name or not email or not message:
            return render(
                request,
                "articles/contact.html",
                {"error": "すべての項目を入力してください。"},
            )

        if len(name) > 100 or len(email) > 254 or len(message) > 5000:
            return render(
                request,
                "articles/contact.html",
                {"error": "入力できる文字数を超えています。"},
            )

        # 確認画面から入力画面に戻る
        if request.POST.get("back") == "yes":
            return render(
                request,
                "articles/contact.html",
                {
                    "name": name,
                    "email": email,
                    "message": message,
                },
            )

        # 確認画面からの最終送信
        if request.POST.get("confirm") == "yes":
            try:
                resend.api_key = os.environ["RESEND_API_KEY"]

                sender = os.environ.get(
                    "RESEND_FROM_EMAIL",
                    "onboarding@resend.dev",
                )

                resend.Emails.send({
                    "from": sender,
                    "to": ["sat0816har@gmail.com"],
                    "reply_to": [email],
                    "subject": f"【すきつな】お問い合わせ：{name}",
                    "text": (
                        f"お名前：{name}\n"
                        f"メールアドレス：{email}\n\n"
                        f"お問い合わせ内容：\n{message}"
                    ),
                })

                # 送信成功
                return render(
                    request,
                    "articles/contact.html",
                    {
                        "success": (
                            "お問い合わせを送信しました。"
                            "ありがとうございます。"
                        ),
                        "clear_form": True,
                    },
                )

            except Exception:
                logger.exception(
                    "お問い合わせメールの送信に失敗しました"
                )

                # 送信失敗時は入力内容を残す
                return render(
                    request,
                    "articles/contact.html",
                    {
                        "error": (
                            "送信に失敗しました。"
                            "時間をおいて再度お試しください。"
                        ),
                        "name": name,
                        "email": email,
                        "message": message,
                    },
                )

        # 最初の送信では、メールを送らず確認画面を表示
        return render(
            request,
            "articles/contact_confirm.html",
            {
                "name": name,
                "email": email,
                "message": message,
            },
        )

    return render(
        request,
        "articles/contact.html",
    )
 



# ご利用ガイド
def guide(request):
    return render(request, "articles/guide.html")




def my_articles(request):
    if not request.user.is_authenticated:
        return redirect("/login/")

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    follower_count = Follow.objects.filter(
    following=request.user,
    follower__is_active=True
    ).count()

    following_count = Follow.objects.filter(
    follower=request.user,
    following__is_active=True
    ).count()

    status = request.GET.get("status", "published")

    articles = Article.objects.filter(
        author=request.user
    )

    if status == "draft":
        articles = articles.filter(
            is_published=False
        )
    else:
        status = "published"
        articles = articles.filter(
            is_published=True
        )

    articles = articles.order_by("-created_at")

    paginator = Paginator(articles, 12)
    page_obj = paginator.get_page(
        request.GET.get("page", 1)
    )

    context = {
        "articles": page_obj.object_list,
        "page_obj": page_obj,
        "has_next": page_obj.has_next(),
        "profile": profile,
        "follower_count": follower_count,
        "following_count": following_count,
        "page_title": f"{request.user.username}さんの投稿",
        "status": status,
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

        profile.website_url = request.POST.get(
            "website_url", ""
        ).strip()

        profile.x_url = request.POST.get(
            "x_url", ""
        ).strip()

        profile.instagram_url = request.POST.get(
            "instagram_url", ""
        ).strip()

        profile.youtube_url = request.POST.get(
            "youtube_url", ""
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
    username=username,
    is_active=True
)

    profile = Profile.objects.filter(
        user=profile_user
    ).first()

    articles = Article.objects.filter(
        author=profile_user,
        is_published=True
    ).order_by("-created_at")

    follower_count = Follow.objects.filter(
    following=profile_user,
    follower__is_active=True
    ).count()

    following_count = Follow.objects.filter(
    follower=profile_user,
    following__is_active=True
    ).count()

    paginator = Paginator(articles, 8)

    page_obj = paginator.get_page(
        request.GET.get("page", 1)
    )

    context = {
    "profile_user": profile_user,
    "profile": profile,
    "follower_count": follower_count,
    "following_count": following_count,
    "articles": page_obj.object_list,
    "page_obj": page_obj,
    "has_next": page_obj.has_next(),
    "is_following": (
        request.user.is_authenticated
        and Follow.objects.filter(
            follower=request.user,
            following=profile_user
        ).exists()
    ),
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




# パスワード再設定メールの送信
def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        users = User.objects.filter(
            email__iexact=email,
            is_active=True,
        )

        for user in users:
            if not user.has_usable_password():
                continue

            try:
                uid = urlsafe_base64_encode(
                    force_bytes(user.pk)
                )

                token = default_token_generator.make_token(user)

                reset_url = request.build_absolute_uri(
                    reverse(
                        "password_reset_confirm",
                        kwargs={
                            "uidb64": uid,
                            "token": token,
                        },
                    )
                )

                resend.api_key = os.environ["RESEND_API_KEY"]

                sender = os.environ.get(
                    "RESEND_FROM_EMAIL",
                    "onboarding@resend.dev",
                )

                resend.Emails.send({
                    "from": sender,
                    "to": [user.email],
                    "subject": "すきつな：パスワード再設定",
                    "text": (
                        f"{user.username} 様\n\n"
                        "パスワード再設定のリクエストを受け付けました。\n"
                        "次のリンクから、新しいパスワードを設定してください。\n\n"
                        f"{reset_url}\n\n"
                        "このメールに心当たりがない場合は、"
                        "このメールを無視してください。\n"
                        "このリンクには有効期限があります。"
                    ),
                })

            except Exception:
                logger.exception(
                    "パスワード再設定メールの送信に失敗しました"
                )

        return redirect("password_reset_done")

    return render(
        request,
        "articles/password_reset_form.html",
    )


# メール送信後の案内画面
def password_reset_done(request):
    return render(
        request,
        "articles/password_reset_done.html",
    )


# 新しいパスワードを設定
def password_reset_confirm(request, uidb64, token):
    user = None
    validlink = False

    try:
        uid = urlsafe_base64_decode(uidb64).decode()

        user = User.objects.get(
            pk=uid,
            is_active=True,
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
        User.DoesNotExist,
    ):
        user = None

    if (
        user is not None
        and default_token_generator.check_token(user, token)
    ):
        validlink = True

        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)

            if form.is_valid():
                form.save()
                return redirect("password_reset_complete")
        else:
            form = SetPasswordForm(user)

    else:
        form = None

    return render(
        request,
        "articles/password_reset_confirm.html",
        {
            "validlink": validlink,
            "form": form,
        },
    )


# パスワード変更完了画面
def password_reset_complete(request):
    return render(
        request,
        "articles/password_reset_complete.html",
    )





def article_ranking(request):
    articles = Article.objects.filter(
        is_published=True,
        author__is_active=True
    ).order_by(
        "-view_count",
        "-created_at"
    )[:10]

    context = {
        "articles": articles,
        "ranking_title": "総合ランキング",
    }

    return render(
        request,
        "articles/ranking_list.html",
        context
    )






def genre_ranking(request, genre_slug):
    articles = Article.objects.filter(
        genre=genre_slug,
        is_published=True,
        author__is_active=True
    ).order_by(
        "-view_count",
        "-created_at"
    )[:10]

    genre_name = dict(
        Article.GENRE_CHOICES
    ).get(genre_slug, "ジャンル別")

    context = {
        "articles": articles,
        "ranking_title": f"{genre_name}ランキング",
        "selected_genre": genre_slug,
        "genre_choices": Article.GENRE_CHOICES,
    }

    return render(
        request,
        "articles/genre_ranking.html",
        context
    )





def category_ranking(request, category_slug):
    articles = Article.objects.filter(
        category=category_slug,
        is_published=True,
        author__is_active=True
    ).order_by(
        "-view_count",
        "-created_at"
    )[:10]

    category_name = dict(
        Article.CATEGORY_CHOICES
    ).get(category_slug, "カテゴリー別")

    context = {
        "articles": articles,
        "ranking_title": f"{category_name}ランキング",
        "selected_category": category_slug,
        "category_choices": Article.CATEGORY_CHOICES,
    }

    return render(
        request,
        "articles/category_ranking.html",
        context
    )




def recent_ranking(request):
    # 7日前の日時を取得
    since = timezone.now() - timedelta(days=7)

    # 直近7日間のいいね数を集計
    articles = Article.objects.filter(
        is_published=True,
        author__is_active=True
    ).annotate(
        recent_like_count=Count(
            "likes",
            filter=Q(likes__created_at__gte=since)
        )
    ).filter(
        recent_like_count__gt=0
    ).order_by(
        "-recent_like_count",
        "-created_at"
    )

    # 最近人気のベスト10を表示
    articles = articles[:10]

    return render(
        request,
        "articles/recent_ranking.html",
        {
            "articles": articles,
            "ranking_title": "最近人気の記事",
        }
    )


# 退会について
def withdrawal(request):
    return render(request, "articles/withdrawal.html")
    
# 退会の確認ページ
@login_required
def withdrawal_confirm_page(request):
    return render(
        request,
        "articles/withdrawal_confirm.html"
    )

# 退会処理
@login_required
@require_POST
def withdrawal_confirm(request):
    user = request.user
    password = request.POST.get("password", "")

    if not user.check_password(password):
        return render(
            request,
            "articles/withdrawal.html",
            {"withdrawal_error": "パスワードが正しくありません。"}
        )

    user.is_active = False
    user.save(update_fields=["is_active"])

    logout(request)

    return redirect("/")


@login_required
@require_POST
def follow_user(request, username):
    target_user = get_object_or_404(
        User,
        username=username
    )

    # 自分自身はフォローできない
    if request.user == target_user:
        return redirect(
            "public_profile",
            username=username
        )

    # すでにフォローしている場合は重複登録しない
    Follow.objects.get_or_create(
        follower=request.user,
        following=target_user
    )

    return redirect(
        "public_profile",
        username=username
    )


@login_required
@require_POST
def unfollow_user(request, username):
    target_user = get_object_or_404(
        User,
        username=username
    )

    # 自分自身はフォロー解除の対象にしない
    if request.user == target_user:
        return redirect(
            "public_profile",
            username=username
        )

    # フォロー関係を削除する
    Follow.objects.filter(
        follower=request.user,
        following=target_user
    ).delete()

    return redirect(
        "public_profile",
        username=username
    )



def follower_list(request, username):
    profile_user = get_object_or_404(
        User,
        username=username
    )

    follows = Follow.objects.filter(
        following=profile_user,
        follower__is_active=True
    ).select_related("follower").order_by("-created_at")

    followers = [
        follow.follower
        for follow in follows
    ]

    context = {
        "profile_user": profile_user,
        "followers": followers,
    }

    return render(
        request,
        "articles/follower_list.html",
        context
    )



def following_list(request, username):
    profile_user = get_object_or_404(
        User,
        username=username
    )

    follows = Follow.objects.filter(
    follower=profile_user,
    following__is_active=True
    ).select_related("following").order_by("-created_at")

    following_users = [
        follow.following
        for follow in follows
    ]

    context = {
        "profile_user": profile_user,
        "following_users": following_users,
    }

    return render(
        request,
        "articles/following_list.html",
        context
    )













