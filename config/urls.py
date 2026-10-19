from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from main import views
from django.contrib.auth import views as auth_views


urlpatterns = [

    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "",
        views.article_list
    ),

       # カテゴリー別ページ
    path(
        "category/<slug:category_slug>/",
        views.category_list,
        name="category_list"
    ),

        # ジャンル別ページ
    path(
        "genre/<slug:genre_slug>/",
        views.genre_list,
        name="genre_list"
    ),

    path(
        "articles/new/",
        views.article_create
    ),

    path(
        "articles/<int:article_id>/",
        views.article_detail
    ),

    path(
        "articles/<int:article_id>/like/",
        views.article_like,
        name="article_like"
    ),

    path(
        "articles/<int:article_id>/edit/",
        views.article_edit
    ),

    path(
        "articles/<int:article_id>/delete/",
        views.article_delete
    ),

    path(
        "register/",
        views.register
    ),

    path(
        "login/",
        views.login_view
    ),

    
    # パスワード再設定
    path(
        "password-reset/",
        views.password_reset_request,
        name="password_reset",
    ),

    path(
        "password-reset/done/",
        views.password_reset_done,
        name="password_reset_done",
    ),

    path(
        "password-reset/<uidb64>/<token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),

    path(
        "password-reset/complete/",
        views.password_reset_complete,
        name="password_reset_complete",
    ),


    path(
    "my-articles/",
    views.my_articles,
    name="my_articles"
    ),

    
    path(
        "profile/edit/",
        views.profile_edit,
        name="profile_edit"
    ),

    
    path(
        "users/<str:username>/",
        views.public_profile,
        name="public_profile"
    ),



    path(
        "logout/",
        views.logout_view
    ),


    path(
        "private-users/", 
        views.user_list, name="user_list"
    ),

    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("guide/", views.guide, name="guide"),

    
]


urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
