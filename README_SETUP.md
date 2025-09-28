# 冷知识小程序 - 后端设置指南

## 项目概述

这是一个基于 Flask 的冷知识小程序后端 API，支持用户投稿、点赞、收藏、评论等功能。

## 技术栈

- **后端**: Python Flask + SQLAlchemy
- **数据库**: MySQL
- **部署**: 腾讯云托管 (Docker)

## 快速开始

### 1. 环境要求

- Python 3.6+
- MySQL 5.7+
- pip

### 2. 安装依赖

```bash
# 进入项目目录
cd coolFacts

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 数据库配置

#### 3.1 设置环境变量

创建 `.env` 文件或设置环境变量：

```bash
# MySQL 配置
MYSQL_USERNAME=root
MYSQL_PASSWORD=your_password
MYSQL_ADDRESS=127.0.0.1:3306

# 可选：数据库名称
MYSQL_DATABASE=coolfacts
```

#### 3.2 初始化数据库

```bash
# 运行数据库初始化脚本
python init_db.py
```

这将创建所有必要的表并插入示例数据。

### 4. 运行应用

#### 方式一：直接运行 Python 脚本
```bash
# 启动 Flask 应用
python run.py 127.0.0.1 8080
```

#### 方式二：使用 Docker（推荐）
```bash
# 开发环境（支持热重载）
docker-compose up --build

# 生产环境
docker build -t coolfacts-backend .
docker run -p 8080:80 coolfacts-backend
```

应用将在 `http://127.0.0.1:8080` 启动。

**注意**: 数据库会在服务器启动时自动初始化，包括：
- 自动创建所有必要的表
- 插入示例数据（如果数据库为空）
- 检查数据库连接状态

数据库初始化逻辑位于 `init_db.py` 中的 `init_database_on_startup()` 函数，`run.py` 会在启动时自动调用此函数。

## API 接口文档

### 冷知识相关

#### 获取随机冷知识
```
GET /api/facts/random
```

#### 获取冷知识列表
```
GET /api/facts/list?page=1&per_page=20
```

#### 创建冷知识
```
POST /api/facts/create
Content-Type: application/json

{
  "openid": "user_openid",
  "nickname": "用户昵称",
  "avatar_url": "头像URL",
  "content": "冷知识内容",
  "image_url": "图片URL（可选）",
  "video_url": "视频URL（可选）"
}
```

#### 点赞冷知识
```
POST /api/facts/{fact_id}/like
Content-Type: application/json

{
  "user_id": 1
}
```

#### 点踩冷知识
```
POST /api/facts/{fact_id}/dislike
Content-Type: application/json

{
  "user_id": 1
}
```

#### 收藏冷知识
```
POST /api/facts/{fact_id}/favorite
Content-Type: application/json

{
  "user_id": 1
}
```

### 评论相关

#### 获取评论列表
```
GET /api/facts/{fact_id}/comments?page=1&per_page=20&user_id=1
```

#### 创建评论
```
POST /api/facts/{fact_id}/comment
Content-Type: application/json

{
  "user_id": 1,
  "content": "评论内容"
}
```

#### 点赞评论
```
POST /api/comments/{comment_id}/like
Content-Type: application/json

{
  "user_id": 1
}
```

### 用户相关

#### 获取用户信息
```
GET /api/user/profile?user_id=1
# 或
GET /api/user/profile?openid=user_openid
```

#### 获取用户收藏
```
GET /api/user/favorites?user_id=1&page=1&per_page=20
```

#### 获取用户发布的冷知识
```
GET /api/user/facts?user_id=1&page=1&per_page=20
```

## 数据库结构

### 主要表结构

1. **users** - 用户表
2. **facts** - 冷知识表
3. **fact_reactions** - 点赞点踩表
4. **favorites** - 收藏表
5. **comments** - 评论表
6. **comment_likes** - 评论点赞表

详细结构请参考 `miaoyunze2025_163/coolFact.md` 文件。

## Docker 部署

### 开发环境（推荐）
使用 `Dockerfile.development` 和 `docker-compose.yml`，支持热重载：

```bash
# 构建并启动服务
docker-compose up --build

# 后台运行
docker-compose up -d --build
```

### 生产环境
使用 `Dockerfile` 构建生产镜像：

```bash
# 构建镜像
docker build -t coolfacts-backend .

# 运行容器
docker run -p 8080:80 coolfacts-backend
```

### Docker Compose 配置
`docker-compose.yml` 已配置：
- 端口映射：`27081:80`
- 环境变量：MySQL 连接配置
- 卷挂载：开发时代码同步

## 开发说明

### 项目结构

```
coolFacts/
├── wxcloudrun/           # 主要应用代码
│   ├── __init__.py      # Flask 应用初始化
│   ├── views.py         # API 路由
│   ├── model.py         # 数据模型
│   ├── dao.py           # 数据访问层
│   └── response.py      # 响应工具
├── init_db.py           # 数据库初始化脚本
├── run.py               # 应用入口
├── config.py            # 配置文件
├── requirements.txt     # Python 依赖
├── Dockerfile           # Docker 配置
├── docker-compose.yml   # Docker Compose 配置
└── README_SETUP.md      # 本文件
```

### 添加新功能

1. 在 `model.py` 中添加新的数据模型
2. 在 `dao.py` 中添加数据访问函数
3. 在 `views.py` 中添加 API 路由
4. 更新数据库：`python init_db.py`

### 调试

启用 Flask 调试模式：

```python
# 在 run.py 中修改
app.run(host=sys.argv[1], port=int(sys.argv[2]), debug=True)
```

## 常见问题

### Q: 数据库连接失败
A: 检查 MySQL 服务是否启动，环境变量是否正确设置。

### Q: 导入模块失败
A: 确保在项目根目录运行，并且虚拟环境已激活。

### Q: API 返回 500 错误
A: 查看控制台日志，通常是数据库连接或 SQL 语法问题。

### Q: 如何添加新的 API 接口
A: 参考现有接口的写法，在 `views.py` 中添加新的路由函数。

## 联系支持

如有问题，请查看项目文档或提交 Issue。
