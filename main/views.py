from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render
)

from .models import Article


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

        username = request.POST["username"]
        password = request.POST["password"]

        User.objects.create_user(
            username=username,
            password=password
        )

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
