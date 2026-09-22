"""
Django 配置文件 —— music_review 项目。

单个配置项的完整含义与取值，查：
https://docs.djangoproject.com/zh-hans/6.0/ref/settings/
"""

from pathlib import Path

# BASE_DIR：项目根目录，其他路径都从它出发拼出来
BASE_DIR = Path(__file__).resolve().parent.parent


# 以下是"开箱即用"的开发配置 —— 不适合直接用于生产环境
# 上线前逐项过一遍部署清单：
# https://docs.djangoproject.com/zh-hans/6.0/howto/deployment/checklist/

# 安全警告：生产环境的密钥必须保密，不能硬编码在代码里
SECRET_KEY = "django-insecure-mp_8rt%@navt1(m!(x!8$9k1%0_ien&9ue++fam6#8k8*$nv_$"

# 安全警告：生产环境绝不能开着 DEBUG 运行（会向访客暴露源码与配置）
DEBUG = True

ALLOWED_HOSTS = []


# 应用注册

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "reviews",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # 练手：请求阶段最后进入（最贴近视图），响应阶段最先返回
    "reviews.middleware.timing_middleware",
]

# 开发期观测面板：SQL 条数/耗时、模板渲染、请求头等，只在 DEBUG 下启用
if DEBUG:
    # 官方建议放 INSTALLED_APPS 最前，至少要排在 staticfiles 之前
    INSTALLED_APPS.insert(0, "debug_toolbar")
    # 放在 SecurityMiddleware 之后，保证面板拿到的响应未被后续中间件改写
    MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")
    # 只对本机发起的请求显示面板
    INTERNAL_IPS = ["127.0.0.1"]

ROOT_URLCONF = "music_review.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # 项目级模板，优先级高于所有应用的模板目录
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

WSGI_APPLICATION = "music_review.wsgi.application"


# 数据库
# https://docs.djangoproject.com/zh-hans/6.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# 密码校验
# https://docs.djangoproject.com/zh-hans/6.0/ref/settings/#auth-password-validators

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


# 国际化
# https://docs.djangoproject.com/zh-hans/6.0/topics/i18n/

LANGUAGE_CODE = "zh-hans"

TIME_ZONE = "Asia/Shanghai"

USE_I18N = True

USE_TZ = True


# 静态文件（CSS、JavaScript、图片）
# https://docs.djangoproject.com/zh-hans/6.0/howto/static-files/

STATIC_URL = "static/"


LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "reviews:home"
LOGOUT_REDIRECT_URL = "reviews:home"
