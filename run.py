# 创建应用实例
import sys

from wxcloudrun import app
from init_db import init_database_on_startup

# 启动Flask Web服务
if __name__ == '__main__':
    # 获取启动参数
    host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    
    print(f"🚀 启动冷知识小程序后端服务...")
    print(f"📍 服务地址: http://{host}:{port}")
    
    # 初始化数据库
    init_database_on_startup()
    
    print(f"🎉 服务器启动完成！")
    print(f"📋 可用的API端点:")
    print(f"   GET  /api/facts/random          - 随机获取冷知识")
    print(f"   GET  /api/facts/list            - 获取冷知识列表") 
    print(f"   POST /api/facts/create          - 创建冷知识")
    print(f"   POST /api/facts/{{id}}/like       - 点赞冷知识")
    print(f"   POST /api/facts/{{id}}/dislike    - 点踩冷知识")
    print(f"   POST /api/facts/{{id}}/favorite   - 收藏冷知识")
    print(f"   GET  /api/facts/{{id}}/comments   - 获取评论")
    print(f"   POST /api/facts/{{id}}/comment    - 创建评论")
    print(f"   POST /api/comments/{{id}}/like    - 点赞评论")
    print(f"   GET  /api/user/profile          - 获取用户信息")
    print(f"   GET  /api/user/favorites        - 获取用户收藏")
    print(f"   GET  /api/user/facts            - 获取用户发布的冷知识")
    
    # 启动服务器
    app.run(host=host, port=port, debug=False)
