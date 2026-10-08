from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


# セキュリティキー
SECRET_KEY = "django-insecure-change-this-later"

# 開発中はTrue
DEBUG = True

# 開発中は空でOK
ALLOWED_HOSTS = []


# アプリケーション
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "main",
]


# ミドルウェア
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
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
            ],
        },
    },
]


# WSGI
WSGI_APPLICATION = "config.wsgi.application"


# データベース
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


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
