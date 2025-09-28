from datetime import datetime
from sqlalchemy import Enum

from wxcloudrun import db


# 计数表
class Counters(db.Model):
    # 设置结构体表格名称
    __tablename__ = 'Counters'

    # 设定结构体对应表格的字段
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=1)
    created_at = db.Column('createdAt', db.TIMESTAMP, nullable=False, default=datetime.now())
    updated_at = db.Column('updatedAt', db.TIMESTAMP, nullable=False, default=datetime.now())


# 用户表
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    openid = db.Column(db.String(64), nullable=False, unique=True, comment='微信openid')
    nickname = db.Column(db.String(64), comment='用户昵称')
    avatar_url = db.Column(db.String(255), comment='头像URL')
    created_at = db.Column(db.TIMESTAMP, default=datetime.now())
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now(), onupdate=datetime.now())
    
    # 关联关系
    facts = db.relationship('Fact', backref='author', lazy='dynamic')
    reactions = db.relationship('FactReaction', backref='user', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    comment_likes = db.relationship('CommentLike', backref='user', lazy='dynamic')


# 冷知识表
class Fact(db.Model):
    __tablename__ = 'facts'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False, comment='发布用户')
    content = db.Column(db.Text, nullable=False, comment='冷知识内容')
    image_url = db.Column(db.String(255), comment='图片URL')
    video_url = db.Column(db.String(255), comment='视频URL')
    status = db.Column(Enum('pending', 'approved', 'rejected', name='fact_status'), 
                      default='pending', comment='审核状态')
    like_count = db.Column(db.Integer, default=0)
    dislike_count = db.Column(db.Integer, default=0)
    favorite_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now())
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now(), onupdate=datetime.now())
    
    # 关联关系
    reactions = db.relationship('FactReaction', backref='fact', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='fact', lazy='dynamic')
    comments = db.relationship('Comment', backref='fact', lazy='dynamic')


# 点赞点踩表
class FactReaction(db.Model):
    __tablename__ = 'fact_reactions'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    fact_id = db.Column(db.BigInteger, db.ForeignKey('facts.id'), nullable=False)
    reaction = db.Column(Enum('like', 'dislike', name='reaction_type'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now())
    
    # 唯一约束
    __table_args__ = (db.UniqueConstraint('user_id', 'fact_id', name='unique_reaction'),)


# 收藏表
class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    fact_id = db.Column(db.BigInteger, db.ForeignKey('facts.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now())
    
    # 唯一约束
    __table_args__ = (db.UniqueConstraint('user_id', 'fact_id', name='unique_fav'),)


# 评论表
class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    fact_id = db.Column(db.BigInteger, db.ForeignKey('facts.id'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    like_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now())
    
    # 关联关系
    likes = db.relationship('CommentLike', backref='comment', lazy='dynamic')


# 评论点赞表
class CommentLike(db.Model):
    __tablename__ = 'comment_likes'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    comment_id = db.Column(db.BigInteger, db.ForeignKey('comments.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now())
    
    # 唯一约束
    __table_args__ = (db.UniqueConstraint('user_id', 'comment_id', name='unique_like'),)
