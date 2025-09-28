#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
创建所有必要的表结构
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from wxcloudrun import app, db
from wxcloudrun.model import (
    Counters, User, Fact, FactReaction, Favorite, Comment, CommentLike
)


def init_database():
    """
    初始化数据库，创建所有表
    """
    with app.app_context():
        try:
            # 创建所有表
            db.create_all()
            print("✅ 数据库表创建成功")
            
            # 插入一些示例数据
            insert_sample_data()
            
        except Exception as e:
            print(f"❌ 数据库初始化失败: {str(e)}")
            return False
    
    return True


def insert_sample_data():
    """
    插入示例数据
    """
    try:
        # 检查是否已有数据
        if User.query.first():
            print("📝 数据库已有数据，跳过示例数据插入")
            return
        
        # 创建示例用户
        user1 = User(
            openid="sample_openid_1",
            nickname="冷知识达人",
            avatar_url="https://example.com/avatar1.jpg"
        )
        user2 = User(
            openid="sample_openid_2", 
            nickname="科普小助手",
            avatar_url="https://example.com/avatar2.jpg"
        )
        
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        
        # 创建示例冷知识
        fact1 = Fact(
            user_id=user1.id,
            content="你知道吗？人的大脑在思考时消耗的能量相当于一个25瓦的灯泡。所以常说'用脑过度'是有科学依据的！",
            status='approved',
            like_count=15,
            dislike_count=2,
            favorite_count=8
        )
        
        fact2 = Fact(
            user_id=user2.id,
            content="香蕉其实是一种浆果！在植物学分类上，香蕉属于浆果类，而草莓反而不是浆果。",
            status='approved', 
            like_count=23,
            dislike_count=1,
            favorite_count=12
        )
        
        fact3 = Fact(
            user_id=user1.id,
            content="人类是唯一会因为情绪而流泪的动物。其他动物的眼泪主要是为了润滑眼球。",
            status='approved',
            like_count=18,
            dislike_count=3,
            favorite_count=6
        )
        
        fact4 = Fact(
            user_id=user2.id,
            content="章鱼有三个心脏！两个负责给鳃供血，一个负责给全身供血。当章鱼游泳时，负责全身供血的心脏会停止跳动。",
            status='approved',
            like_count=31,
            dislike_count=0,
            favorite_count=19
        )
        
        fact5 = Fact(
            user_id=user1.id,
            content="蜜蜂的翅膀每分钟可以扇动200次！这就是为什么我们能听到嗡嗡声的原因。",
            status='approved',
            like_count=12,
            dislike_count=1,
            favorite_count=7
        )
        
        db.session.add(fact1)
        db.session.add(fact2) 
        db.session.add(fact3)
        db.session.add(fact4)
        db.session.add(fact5)
        db.session.commit()
        
        # 创建示例评论
        comment1 = Comment(
            fact_id=fact1.id,
            user_id=user2.id,
            content="原来如此！难怪学习久了会累，大脑在'发光发热'啊！",
            like_count=3
        )
        
        comment2 = Comment(
            fact_id=fact2.id,
            user_id=user1.id,
            content="涨知识了！那番茄也是浆果吗？",
            like_count=1
        )
        
        comment3 = Comment(
            fact_id=fact4.id,
            user_id=user1.id,
            content="章鱼真的很神奇，三个心脏！",
            like_count=2
        )
        
        db.session.add(comment1)
        db.session.add(comment2)
        db.session.add(comment3)
        db.session.commit()
        
        print("✅ 示例数据插入成功")
        print(f"   - 创建了 {User.query.count()} 个用户")
        print(f"   - 创建了 {Fact.query.count()} 条冷知识")
        print(f"   - 创建了 {Comment.query.count()} 条评论")
        
    except Exception as e:
        print(f"❌ 示例数据插入失败: {str(e)}")
        db.session.rollback()


def init_database_on_startup():
    """
    启动时初始化数据库（供run.py调用）
    """
    with app.app_context():
        try:
            # 尝试查询users表来检查数据库是否已初始化
            try:
                User.query.first()
                print("📝 数据库已存在，跳过初始化")
            except Exception:
                # 如果查询失败，说明表不存在，需要初始化
                print("🚀 检测到新数据库，开始初始化...")
                
                # 创建所有表
                db.create_all()
                print("✅ 数据库表创建成功")
                
                # 插入示例数据
                insert_sample_data()
                
        except Exception as e:
            print(f"❌ 数据库初始化失败: {str(e)}")
            # 不阻止服务器启动，但记录错误


def drop_all_tables():
    """
    删除所有表（谨慎使用！）
    """
    with app.app_context():
        try:
            db.drop_all()
            print("🗑️  所有表已删除")
        except Exception as e:
            print(f"❌ 删除表失败: {str(e)}")


if __name__ == '__main__':
    print("🚀 开始初始化数据库...")
    
    if len(sys.argv) > 1 and sys.argv[1] == '--drop':
        # 删除所有表
        drop_all_tables()
        print("重新创建表...")
    
    success = init_database()
    
    if success:
        print("🎉 数据库初始化完成！")
        print("\n📋 可用的API端点:")
        print("   GET  /api/facts/random          - 随机获取冷知识")
        print("   GET  /api/facts/list            - 获取冷知识列表") 
        print("   POST /api/facts/create          - 创建冷知识")
        print("   POST /api/facts/{id}/like       - 点赞冷知识")
        print("   POST /api/facts/{id}/dislike    - 点踩冷知识")
        print("   POST /api/facts/{id}/favorite   - 收藏冷知识")
        print("   GET  /api/facts/{id}/comments   - 获取评论")
        print("   POST /api/facts/{id}/comment    - 创建评论")
        print("   POST /api/comments/{id}/like    - 点赞评论")
        print("   GET  /api/user/profile          - 获取用户信息")
        print("   GET  /api/user/favorites        - 获取用户收藏")
        print("   GET  /api/user/facts            - 获取用户发布的冷知识")
    else:
        print("💥 数据库初始化失败！")
        sys.exit(1)
