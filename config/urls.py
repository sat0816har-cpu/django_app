from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from main import views


urlpatterns = [

    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "",
        views.article_list
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

    path(
        "logout/",
        views.logout_view
    ),
]


urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
