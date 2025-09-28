import logging
from datetime import datetime
from sqlalchemy.exc import OperationalError
from sqlalchemy import func, and_, or_

from wxcloudrun import db
from wxcloudrun.model import Counters, User, Fact, FactReaction, Favorite, Comment, CommentLike

# 初始化日志
logger = logging.getLogger('log')


def query_counterbyid(id):
    """
    根据ID查询Counter实体
    :param id: Counter的ID
    :return: Counter实体
    """
    try:
        return Counters.query.filter(Counters.id == id).first()
    except OperationalError as e:
        logger.info("query_counterbyid errorMsg= {} ".format(e))
        return None


def delete_counterbyid(id):
    """
    根据ID删除Counter实体
    :param id: Counter的ID
    """
    try:
        counter = Counters.query.get(id)
        if counter is None:
            return
        db.session.delete(counter)
        db.session.commit()
    except OperationalError as e:
        logger.info("delete_counterbyid errorMsg= {} ".format(e))


def insert_counter(counter):
    """
    插入一个Counter实体
    :param counter: Counters实体
    """
    try:
        db.session.add(counter)
        db.session.commit()
    except OperationalError as e:
        logger.info("insert_counter errorMsg= {} ".format(e))


def update_counterbyid(counter):
    """
    根据ID更新counter的值
    :param counter实体
    """
    try:
        counter = query_counterbyid(counter.id)
        if counter is None:
            return
        db.session.flush()
        db.session.commit()
    except OperationalError as e:
        logger.info("update_counterbyid errorMsg= {} ".format(e))


def set_counterbyid(id, count_value):
    """
    根据ID设置counter的值
    :param id: Counter的ID
    :param count_value: 要设置的值
    """
    try:
        counter = query_counterbyid(id)
        if counter is None:
            # 如果不存在，创建新的counter
            counter = Counters()
            counter.id = id
            counter.count = count_value
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            # 如果存在，更新值
            counter.count = count_value
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
    except OperationalError as e:
        logger.info("set_counterbyid errorMsg= {} ".format(e))


# ==================== 用户相关 DAO ====================

def create_or_get_user(openid, nickname=None, avatar_url=None):
    """
    创建或获取用户
    """
    try:
        user = User.query.filter_by(openid=openid).first()
        if user is None:
            user = User(openid=openid, nickname=nickname, avatar_url=avatar_url)
            db.session.add(user)
            db.session.commit()
        elif nickname or avatar_url:
            # 更新用户信息
            if nickname:
                user.nickname = nickname
            if avatar_url:
                user.avatar_url = avatar_url
            user.updated_at = datetime.now()
            db.session.commit()
        return user
    except OperationalError as e:
        logger.info("create_or_get_user errorMsg= {} ".format(e))
        return None


def get_user_by_id(user_id):
    """
    根据ID获取用户
    """
    try:
        return User.query.get(user_id)
    except OperationalError as e:
        logger.info("get_user_by_id errorMsg= {} ".format(e))
        return None


# ==================== 冷知识相关 DAO ====================

def create_fact(user_id, content, image_url=None, video_url=None):
    """
    创建冷知识
    """
    try:
        fact = Fact(
            user_id=user_id,
            content=content,
            image_url=image_url,
            video_url=video_url
        )
        db.session.add(fact)
        db.session.commit()
        return fact
    except OperationalError as e:
        logger.info("create_fact errorMsg= {} ".format(e))
        return None


def get_facts_list(status='approved', page=1, per_page=20):
    """
    获取冷知识列表
    """
    try:
        query = Fact.query.filter_by(status=status)
        return query.order_by(Fact.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    except OperationalError as e:
        logger.info("get_facts_list errorMsg= {} ".format(e))
        return None


def get_random_fact():
    """
    随机获取一条已审核的冷知识
    """
    try:
        return Fact.query.filter_by(status='approved').order_by(func.random()).first()
    except OperationalError as e:
        logger.info("get_random_fact errorMsg= {} ".format(e))
        return None


def get_fact_by_id(fact_id):
    """
    根据ID获取冷知识
    """
    try:
        return Fact.query.get(fact_id)
    except OperationalError as e:
        logger.info("get_fact_by_id errorMsg= {} ".format(e))
        return None


def get_user_facts(user_id, page=1, per_page=20):
    """
    获取用户发布的冷知识
    """
    try:
        return Fact.query.filter_by(user_id=user_id).order_by(
            Fact.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
    except OperationalError as e:
        logger.info("get_user_facts errorMsg= {} ".format(e))
        return None


# ==================== 点赞点踩相关 DAO ====================

def add_fact_reaction(user_id, fact_id, reaction_type):
    """
    添加点赞或点踩
    """
    try:
        # 检查是否已有反应
        existing = FactReaction.query.filter_by(
            user_id=user_id, fact_id=fact_id
        ).first()
        
        if existing:
            # 如果反应类型相同，删除反应
            if existing.reaction == reaction_type:
                db.session.delete(existing)
                # 更新计数
                fact = Fact.query.get(fact_id)
                if reaction_type == 'like':
                    fact.like_count = max(0, fact.like_count - 1)
                else:
                    fact.dislike_count = max(0, fact.dislike_count - 1)
            else:
                # 更新反应类型
                old_reaction = existing.reaction
                existing.reaction = reaction_type
                # 更新计数
                fact = Fact.query.get(fact_id)
                if old_reaction == 'like':
                    fact.like_count = max(0, fact.like_count - 1)
                    fact.dislike_count += 1
                else:
                    fact.dislike_count = max(0, fact.dislike_count - 1)
                    fact.like_count += 1
        else:
            # 创建新反应
            reaction = FactReaction(
                user_id=user_id,
                fact_id=fact_id,
                reaction=reaction_type
            )
            db.session.add(reaction)
            # 更新计数
            fact = Fact.query.get(fact_id)
            if reaction_type == 'like':
                fact.like_count += 1
            else:
                fact.dislike_count += 1
        
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("add_fact_reaction errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def get_user_fact_reaction(user_id, fact_id):
    """
    获取用户对冷知识的反应
    """
    try:
        return FactReaction.query.filter_by(
            user_id=user_id, fact_id=fact_id
        ).first()
    except OperationalError as e:
        logger.info("get_user_fact_reaction errorMsg= {} ".format(e))
        return None


# ==================== 收藏相关 DAO ====================

def add_favorite(user_id, fact_id):
    """
    添加收藏
    """
    try:
        # 检查是否已收藏
        existing = Favorite.query.filter_by(
            user_id=user_id, fact_id=fact_id
        ).first()
        
        if existing:
            # 取消收藏
            db.session.delete(existing)
            fact = Fact.query.get(fact_id)
            fact.favorite_count = max(0, fact.favorite_count - 1)
            result = False
        else:
            # 添加收藏
            favorite = Favorite(user_id=user_id, fact_id=fact_id)
            db.session.add(favorite)
            fact = Fact.query.get(fact_id)
            fact.favorite_count += 1
            result = True
        
        db.session.commit()
        return result
    except OperationalError as e:
        logger.info("add_favorite errorMsg= {} ".format(e))
        db.session.rollback()
        return None


def get_user_favorites(user_id, page=1, per_page=20):
    """
    获取用户收藏的冷知识
    """
    try:
        return db.session.query(Fact).join(Favorite).filter(
            Favorite.user_id == user_id, Fact.status == 'approved'
        ).order_by(Favorite.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    except OperationalError as e:
        logger.info("get_user_favorites errorMsg= {} ".format(e))
        return None


def is_favorited(user_id, fact_id):
    """
    检查用户是否收藏了某条冷知识
    """
    try:
        return Favorite.query.filter_by(
            user_id=user_id, fact_id=fact_id
        ).first() is not None
    except OperationalError as e:
        logger.info("is_favorited errorMsg= {} ".format(e))
        return False


# ==================== 评论相关 DAO ====================

def create_comment(fact_id, user_id, content):
    """
    创建评论
    """
    try:
        comment = Comment(
            fact_id=fact_id,
            user_id=user_id,
            content=content
        )
        db.session.add(comment)
        db.session.commit()
        return comment
    except OperationalError as e:
        logger.info("create_comment errorMsg= {} ".format(e))
        return None


def get_fact_comments(fact_id, page=1, per_page=20):
    """
    获取冷知识的评论列表
    """
    try:
        return Comment.query.filter_by(fact_id=fact_id).order_by(
            Comment.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
    except OperationalError as e:
        logger.info("get_fact_comments errorMsg= {} ".format(e))
        return None


def like_comment(user_id, comment_id):
    """
    点赞评论
    """
    try:
        # 检查是否已点赞
        existing = CommentLike.query.filter_by(
            user_id=user_id, comment_id=comment_id
        ).first()
        
        if existing:
            # 取消点赞
            db.session.delete(existing)
            comment = Comment.query.get(comment_id)
            comment.like_count = max(0, comment.like_count - 1)
            result = False
        else:
            # 添加点赞
            like = CommentLike(user_id=user_id, comment_id=comment_id)
            db.session.add(like)
            comment = Comment.query.get(comment_id)
            comment.like_count += 1
            result = True
        
        db.session.commit()
        return result
    except OperationalError as e:
        logger.info("like_comment errorMsg= {} ".format(e))
        db.session.rollback()
        return None


def is_comment_liked(user_id, comment_id):
    """
    检查用户是否点赞了某条评论
    """
    try:
        return CommentLike.query.filter_by(
            user_id=user_id, comment_id=comment_id
        ).first() is not None
    except OperationalError as e:
        logger.info("is_comment_liked errorMsg= {} ".format(e))
        return False