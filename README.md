# 🎵 Music Review · 乐评网

一个用 Django 从零搭建的专辑乐评网站：收录专辑信息、展示专业乐评人评分与长评、并支持普通用户打分。

> 这是我系统学习 Django 的实践项目，跟随官方教程 Part 1–7 逐步构建，并在此基础上扩展了搜索、多维度筛选、封面自动抓取和后台定制等功能。

---

## ✨ 功能

- **专辑列表**：网格布局展示全部专辑，无封面时显示占位图
- **关键词搜索**：标题与艺人名同时匹配（`Q` 对象实现 OR 查询，不区分大小写）
- **专辑详情**：基础信息 + 乐评人长评 + 用户评分列表与平均分
- **按艺人筛选**：点击艺人名查看其全部专辑
- **按乐评人筛选**：点击乐评人姓名查看其撰写的全部乐评
- **封面自动抓取**：调用 iTunes Search API 按「艺人 + 专辑名」检索并保存 1000×1000 高清封面，无需申请密钥
- **后台管理**：自定义列表字段、封面缩略图预览、评分区间过滤器、字段分组、保存时自动补全乐评人

## 🛠 技术栈

| 类别 | 选型 |
|---|---|
| 语言 | Python 3.13 |
| 框架 | Django 6.0 |
| 数据库 | SQLite（开发阶段） |
| 外部接口 | iTunes Search API |
| 代码规范 | black + ruff |

## 🚀 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/Percy-Lotty/music_review.git
cd music_review

# 2. 创建并激活虚拟环境
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库
python manage.py migrate

# 5. 导入示例数据（可选，13 张专辑与用户评分）
python manage.py loaddata seed_data

# 6. 创建后台管理员
python manage.py createsuperuser

# 7. 启动开发服务器
python manage.py runserver
```

打开 http://127.0.0.1:8000/ 查看首页，http://127.0.0.1:8000/admin/ 进入后台录入数据。

示例数据存放在 `reviews/fixtures/seed_data.json`，执行第 5 步即可把专辑、乐评与用户评分一次性导入任意一台机器的空数据库。导入前需先完成 `migrate`；重复执行会按主键覆盖，不会产生重复记录。

## 📁 项目结构

```
music_review/
├── manage.py
├── requirements.txt
├── pyproject.toml              # ruff 配置
├── docs/                       # 学习文档归档
│   ├── Django教程Part1-7复习文档.html
│   └── notes.html              # 学习笔记
├── music_review/               # 项目配置
│   ├── settings.py
│   ├── urls.py                 # 根路由，include 到 reviews
│   ├── asgi.py
│   └── wsgi.py
└── reviews/                    # 核心应用
    ├── models.py               # Album / UserRating
    ├── views.py                # 4 个视图
    ├── urls.py                 # 应用路由
    ├── admin.py                # 后台定制
    ├── migrations/             # 数据库迁移记录
    ├── fixtures/
    │   └── seed_data.json      # 示例数据（loaddata 导入）
    └── templates/reviews/      # 模板
```

## 🗂 数据模型

**Album（专辑）**

| 字段 | 类型 | 说明 |
|---|---|---|
| `title` / `artist` | CharField | 专辑名 / 艺人 |
| `release_date` | DateField | 发行日期 |
| `cover_url` | URLField | 封面地址，可由 iTunes API 自动填充 |
| `genre` / `label` | CharField | 风格 / 厂牌 |
| `critic_score` | IntegerField | 乐评人评分 0–100 |
| `critic_review` | TextField | 乐评正文 |
| `critic_name` | CharField | 乐评人姓名 |
| `critic_published_at` | DateField | 乐评发布时间 |

**UserRating（用户评分）**

| 字段 | 类型 | 说明 |
|---|---|---|
| `album` | ForeignKey → Album | 级联删除，反向名 `ratings` |
| `score` | IntegerField | 用户评分 0–10 |
| `reviewer_name` | CharField | 评分者昵称，可为空 |
| `created_at` | DateTimeField | 自动记录创建时间 |

> 设计说明：乐评字段内联在 `Album` 上而非独立建表——一张专辑最多对应一份专业乐评，拆表只会多一次连表查询。

## 🧹 代码规范

项目用 black 统一格式、ruff 做静态检查，两者安装在 `requirements-dev.txt`。它们职责不同，**不能互相替代**：black 只负责排版（缩进、引号、折行），ruff 负责发现问题（未使用的导入、导入排序、未定义名称等）。

每次写完代码，提交前依次执行：

```bash
# 1. 静态检查（可自动修复的问题顺手修掉）
ruff check . --fix

# 2. 统一格式
black .

# 3. Django 自身的配置检查
python manage.py check

# 4. 跑测试（改动了逻辑时必跑）
python manage.py test
```

第 4 条只在改动逻辑时需要；前三条每次提交都应跑。四条都没有输出或报错，再 `git add` / `git commit`。嫌麻烦时可以记成一行：

```bash
ruff check . --fix && black .
```

配置固定在 `pyproject.toml`：black 与 ruff 的 `line-length` 都是 88，`migrations/` 目录两边统一排除（迁移文件由 Django 生成，不手工调整格式）。

## 🗺 后续计划

- [ ] 用户系统：注册 / 登录 / 登出，评分与账号关联
- [ ] 一人一专辑仅可评分一次（`UniqueConstraint`）
- [ ] 个人中心：查看本人全部评分记录
- [x] 函数视图改写为类视图（CBV）+ 列表分页
- [ ] 补充自动化测试
- [ ] ORM 查询优化（`select_related` / `annotate` 消除 N+1）
- [ ] Django REST Framework 提供 API
- [ ] 部署上线（Nginx + Gunicorn）

## 📄 License

本项目仅用于学习目的。专辑封面图片版权归各唱片公司所有。
