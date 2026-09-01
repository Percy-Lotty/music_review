"""
music_review 项目的 WSGI 配置。

部署时，WSGI 服务器（如 Gunicorn、uWSGI）加载的就是本模块
名为 ``application`` 的可调用对象。

详细说明见：
https://docs.djangoproject.com/zh-hans/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "music_review.settings")

application = get_wsgi_application()
