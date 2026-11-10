import os

from dotenv import load_dotenv

from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR.parent / ".env")


# セキュリティキーはRenderの環境変数から取得
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

if not SECRET_KEY:
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY が設定されていません。"
    )

# 本番環境ではFalseにする
DEBUG = (
    os.environ.get("DJANGO_DEBUG", "False").lower() == "true"
)

# 公開サイトのドメイン
ALLOWED_HOSTS = [
    "django-app-crtr.onrender.com",
    "sukitsuna.com",
    "www.sukitsuna.com",
]

# HTTPSで利用する場合のCookie保護
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CSRF_TRUSTED_ORIGINS = [
    "https://sukitsuna.com",
    "https://www.sukitsuna.com",
]

CSRF_FAILURE_VIEW = "main.views.custom_csrf_failure"


# アプリケーション

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",


    "main",
]



# ミドルウェア
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# URL設定
ROOT_URLCONF = "config.urls"


# テンプレート
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates",
        ],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                
                "main.context_processors.sidebar_sub_categories",
            ],
        },
    },
]


# WSGI
WSGI_APPLICATION = "config.wsgi.application"



# データベース
import dj_database_url
import os

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

if os.environ.get("DATABASE_URL"):
    DATABASES["default"] = dj_database_url.config(
        conn_max_age=600,
        ssl_require=True,
    )


# パスワードのバリデーション
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# 言語
LANGUAGE_CODE = "ja"

# タイムゾーン
TIME_ZONE = "Asia/Tokyo"

USE_I18N = True
USE_TZ = True


# 静的ファイル
STATIC_URL = "static/"


# アップロードした画像など
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# デフォルトの主キー
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# css設定
STATIC_URL = "/static/"

STATICFILES_DIRS = [BASE_DIR / "static"]

STATIC_ROOT = BASE_DIR / "staticfiles"


# Gmailによるメール送信設定
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))

EMAIL_USE_TLS = (
    os.environ.get("EMAIL_USE_TLS", "True").lower() == "true"
)

EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")

DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    EMAIL_HOST_USER
)

# メール送信のタイムアウトを10秒に設定
EMAIL_TIMEOUT = 10


STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# 操作が30分間なければセッションを終了する
SESSION_COOKIE_AGE = 1800

# ブラウザを閉じても、30分間はセッションを維持する
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# 操作するたびにセッションの有効期限を更新する
SESSION_SAVE_EVERY_REQUEST = True

# エラー発生時の管理者通知
ADMINS = [
    ("管理者", "sukitsuna.info@gmail.com"),
]

SERVER_EMAIL = DEFAULT_FROM_EMAIL

