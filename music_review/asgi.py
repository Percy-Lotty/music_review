"""
music_review 项目的 ASGI 配置。

部署时，ASGI 服务器（如 Daphne、Uvicorn）加载的就是本模块
名为 ``application`` 的可调用对象。

详细说明见：
https://docs.djangoproject.com/zh-hans/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "music_review.settings")

application = get_asgi_application()
