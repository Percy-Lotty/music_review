"""计时中间件：把每个请求的耗时写进响应头 X-Response-Time-ms。

函数式中间件的三段结构：
  1. 外层函数只在服务器启动时执行一次（工厂）；
  2. get_response 调用之前的代码 = 请求阶段（洋葱由外向内）；
  3. get_response 调用之后的代码 = 响应阶段（洋葱由内向外）。
"""

import time


def timing_middleware(get_response):
    # 这里的代码只在启动时执行一次；get_response 代表"下一层"，最终通向视图

    def middleware(request):
        start = time.perf_counter()

        response = get_response(request)  # ← 调用下一层（最终是视图）

        cost = (time.perf_counter() - start) * 1000
        response["X-Response-Time-ms"] = f"{cost:.1f}"
        return response

    return middleware
