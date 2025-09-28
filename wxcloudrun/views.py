from datetime import datetime
from flask import render_template, request, jsonify
from run import app
from wxcloudrun.dao import (
    # Counter functions
    delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid, set_counterbyid,
    # User functions
    create_or_get_user, get_user_by_id,
    # Fact functions
    create_fact, get_facts_list, get_random_fact, get_fact_by_id, get_user_facts,
    # Reaction functions
    add_fact_reaction, get_user_fact_reaction,
    # Favorite functions
    add_favorite, get_user_favorites, is_favorited,
    # Comment functions
    create_comment, get_fact_comments, like_comment, is_comment_liked
)
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response


@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')


@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)


@app.route('/api/count/set', methods=['POST'])
def set_count():
    """
    :return: 设置计数的值
    """
    # 获取请求体参数
    params = request.get_json()
    
    # 检查count参数
    if 'count' not in params:
        return make_err_response('缺少count参数')
    
    try:
        count_value = int(params['count'])
        if count_value < 0:
            return make_err_response('count值不能为负数')
        
        # 设置count值
        set_counterbyid(1, count_value)
        
        # 返回设置后的值
        counter = query_counterbyid(1)
        return make_succ_response(counter.count if counter else 0)
        
    except ValueError:
        return make_err_response('count参数必须是数字')
    except Exception as e:
        return make_err_response(f'设置失败: {str(e)}')


@app.route('/api/count/reset', methods=['POST'])
def reset_count():
    """
    :return: 重置计数为0
    """
    try:
        # 设置count值为0
        set_counterbyid(1, 0)
        
        # 返回重置后的值
        return make_succ_response(0)
        
    except Exception as e:
        return make_err_response(f'重置失败: {str(e)}')


# ==================== 冷知识 API ====================

@app.route('/api/facts/random', methods=['GET'])
def get_random_fact_api():
    """
    随机获取冷知识
    """
    try:
        fact = get_random_fact()
        if fact:
            return make_succ_response({
                'id': fact.id,
                'content': fact.content,
                'image_url': fact.image_url,
                'video_url': fact.video_url,
                'like_count': fact.like_count,
                'dislike_count': fact.dislike_count,
                'favorite_count': fact.favorite_count,
                'created_at': fact.created_at.isoformat(),
                'author': {
                    'id': fact.author.id,
                    'nickname': fact.author.nickname,
                    'avatar_url': fact.author.avatar_url
                }
            })
        else:
            return make_err_response('暂无冷知识')
    except Exception as e:
        return make_err_response(f'获取失败: {str(e)}')


@app.route('/api/facts/list', methods=['GET'])
def get_facts_list_api():
    """
    获取冷知识列表
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category', '')
        sort = request.args.get('sort', 'latest')  # latest, popular
        
        facts_pagination = get_facts_list(status='approved', page=page, per_page=per_page)
        
        if facts_pagination:
            facts_data = []
            for fact in facts_pagination.items:
                facts_data.append({
                    'id': fact.id,
                    'content': fact.content,
                    'image_url': fact.image_url,
                    'video_url': fact.video_url,
                    'like_count': fact.like_count,
                    'dislike_count': fact.dislike_count,
                    'favorite_count': fact.favorite_count,
                    'created_at': fact.created_at.isoformat(),
                    'author': {
                        'id': fact.author.id,
                        'nickname': fact.author.nickname,
                        'avatar_url': fact.author.avatar_url
                    }
                })
            
            return make_succ_response({
                'facts': facts_data,
                'pagination': {
                    'page': facts_pagination.page,
                    'pages': facts_pagination.pages,
                    'per_page': facts_pagination.per_page,
                    'total': facts_pagination.total,
                    'has_next': facts_pagination.has_next,
                    'has_prev': facts_pagination.has_prev
                }
            })
        else:
            return make_err_response('获取列表失败')
    except Exception as e:
        return make_err_response(f'获取失败: {str(e)}')


@app.route('/api/facts/create', methods=['POST'])
def create_fact_api():
    """
    创建冷知识
    """
    try:
        params = request.get_json()
        
        # 验证必要参数
        if not params or 'openid' not in params or 'content' not in params:
            return make_err_response('缺少必要参数')
        
        openid = params['openid']
        content = params['content']
        image_url = params.get('image_url')
        video_url = params.get('video_url')
        
        # 验证内容长度
        if len(content.strip()) < 10:
            return make_err_response('冷知识内容至少需要10个字符')
        
        # 获取或创建用户
        user = create_or_get_user(openid, params.get('nickname'), params.get('avatar_url'))
        if not user:
            return make_err_response('用户创建失败')
        
        # 创建冷知识
        fact = create_fact(user.id, content, image_url, video_url)
        if fact:
            return make_succ_response({
                'id': fact.id,
                'content': fact.content,
                'status': fact.status,
                'created_at': fact.created_at.isoformat()
            })
        else:
            return make_err_response('创建失败')
    except Exception as e:
        return make_err_response(f'创建失败: {str(e)}')


@app.route('/api/facts/<int:fact_id>/like', methods=['POST'])
def like_fact_api(fact_id):
    """
    点赞冷知识
    """
    try:
        params = request.get_json()
        if not params or 'user_id' not in params:
            return make_err_response('缺少用户ID')
        
        user_id = params['user_id']
        success = add_fact_reaction(user_id, fact_id, 'like')
        
        if success is not None:
            fact = get_fact_by_id(fact_id)
            return make_succ_response({
                'liked': success,
                'like_count': fact.like_count if fact else 0,
                'dislike_count': fact.dislike_count if fact else 0
            })
        else:
            return make_err_response('操作失败')
    except Exception as e:
        return make_err_response(f'操作失败: {str(e)}')


@app.route('/api/facts/<int:fact_id>/dislike', methods=['POST'])
def dislike_fact_api(fact_id):
    """
    点踩冷知识
    """
    try:
        params = request.get_json()
        if not params or 'user_id' not in params:
            return make_err_response('缺少用户ID')
        
        user_id = params['user_id']
        success = add_fact_reaction(user_id, fact_id, 'dislike')
        
        if success is not None:
            fact = get_fact_by_id(fact_id)
            return make_succ_response({
                'disliked': success,
                'like_count': fact.like_count if fact else 0,
                'dislike_count': fact.dislike_count if fact else 0
            })
        else:
            return make_err_response('操作失败')
    except Exception as e:
        return make_err_response(f'操作失败: {str(e)}')


@app.route('/api/facts/<int:fact_id>/favorite', methods=['POST'])
def favorite_fact_api(fact_id):
    """
    收藏冷知识
    """
    try:
        params = request.get_json()
        if not params or 'user_id' not in params:
            return make_err_response('缺少用户ID')
        
        user_id = params['user_id']
        result = add_favorite(user_id, fact_id)
        
        if result is not None:
            fact = get_fact_by_id(fact_id)
            return make_succ_response({
                'favorited': result,
                'favorite_count': fact.favorite_count if fact else 0
            })
        else:
            return make_err_response('操作失败')
    except Exception as e:
        return make_err_response(f'操作失败: {str(e)}')


# ==================== 评论 API ====================

@app.route('/api/facts/<int:fact_id>/comments', methods=['GET'])
def get_fact_comments_api(fact_id):
    """
    获取冷知识评论
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        user_id = request.args.get('user_id', type=int)
        
        comments_pagination = get_fact_comments(fact_id, page=page, per_page=per_page)
        
        if comments_pagination:
            comments_data = []
            for comment in comments_pagination.items:
                is_liked = False
                if user_id:
                    is_liked = is_comment_liked(user_id, comment.id)
                
                comments_data.append({
                    'id': comment.id,
                    'content': comment.content,
                    'like_count': comment.like_count,
                    'is_liked': is_liked,
                    'created_at': comment.created_at.isoformat(),
                    'author': {
                        'id': comment.user.id,
                        'nickname': comment.user.nickname,
                        'avatar_url': comment.user.avatar_url
                    }
                })
            
            return make_succ_response({
                'comments': comments_data,
                'pagination': {
                    'page': comments_pagination.page,
                    'pages': comments_pagination.pages,
                    'per_page': comments_pagination.per_page,
                    'total': comments_pagination.total,
                    'has_next': comments_pagination.has_next,
                    'has_prev': comments_pagination.has_prev
                }
            })
        else:
            return make_err_response('获取评论失败')
    except Exception as e:
        return make_err_response(f'获取失败: {str(e)}')


@app.route('/api/facts/<int:fact_id>/comment', methods=['POST'])
def create_comment_api(fact_id):
    """
    创建评论
    """
    try:
        params = request.get_json()
        if not params or 'user_id' not in params or 'content' not in params:
            return make_err_response('缺少必要参数')
        
        user_id = params['user_id']
        content = params['content']
        
        if len(content.strip()) < 1:
            return make_err_response('评论内容不能为空')
        
        comment = create_comment(fact_id, user_id, content)
        if comment:
            return make_succ_response({
                'id': comment.id,
                'content': comment.content,
                'like_count': comment.like_count,
                'created_at': comment.created_at.isoformat()
            })
        else:
            return make_err_response('评论失败')
    except Exception as e:
        return make_err_response(f'评论失败: {str(e)}')


@app.route('/api/comments/<int:comment_id>/like', methods=['POST'])
def like_comment_api(comment_id):
    """
    点赞评论
    """
    try:
        params = request.get_json()
        if not params or 'user_id' not in params:
            return make_err_response('缺少用户ID')
        
        user_id = params['user_id']
        result = like_comment(user_id, comment_id)
        
        if result is not None:
            return make_succ_response({
                'liked': result
            })
        else:
            return make_err_response('操作失败')
    except Exception as e:
        return make_err_response(f'操作失败: {str(e)}')


# ==================== 用户 API ====================

@app.route('/api/user/profile', methods=['GET'])
def get_user_profile_api():
    """
    获取用户信息
    """
    try:
        user_id = request.args.get('user_id', type=int)
        openid = request.args.get('openid')
        
        if user_id:
            user = get_user_by_id(user_id)
        elif openid:
            user = create_or_get_user(openid)
        else:
            return make_err_response('缺少用户标识')
        
        if user:
            return make_succ_response({
                'id': user.id,
                'openid': user.openid,
                'nickname': user.nickname,
                'avatar_url': user.avatar_url,
                'created_at': user.created_at.isoformat()
            })
        else:
            return make_err_response('用户不存在')
    except Exception as e:
        return make_err_response(f'获取失败: {str(e)}')


@app.route('/api/user/favorites', methods=['GET'])
def get_user_favorites_api():
    """
    获取用户收藏
    """
    try:
        user_id = request.args.get('user_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        if not user_id:
            return make_err_response('缺少用户ID')
        
        favorites_pagination = get_user_favorites(user_id, page=page, per_page=per_page)
        
        if favorites_pagination:
            facts_data = []
            for fact in favorites_pagination.items:
                facts_data.append({
                    'id': fact.id,
                    'content': fact.content,
                    'image_url': fact.image_url,
                    'video_url': fact.video_url,
                    'like_count': fact.like_count,
                    'dislike_count': fact.dislike_count,
                    'favorite_count': fact.favorite_count,
                    'created_at': fact.created_at.isoformat(),
                    'author': {
                        'id': fact.author.id,
                        'nickname': fact.author.nickname,
                        'avatar_url': fact.author.avatar_url
                    }
                })
            
            return make_succ_response({
                'favorites': facts_data,
                'pagination': {
                    'page': favorites_pagination.page,
                    'pages': favorites_pagination.pages,
                    'per_page': favorites_pagination.per_page,
                    'total': favorites_pagination.total,
                    'has_next': favorites_pagination.has_next,
                    'has_prev': favorites_pagination.has_prev
                }
            })
        else:
            return make_err_response('获取收藏失败')
    except Exception as e:
        return make_err_response(f'获取失败: {str(e)}')


@app.route('/api/user/facts', methods=['GET'])
def get_user_facts_api():
    """
    获取用户发布的冷知识
    """
    try:
        user_id = request.args.get('user_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        if not user_id:
            return make_err_response('缺少用户ID')
        
        facts_pagination = get_user_facts(user_id, page=page, per_page=per_page)
        
        if facts_pagination:
            facts_data = []
            for fact in facts_pagination.items:
                facts_data.append({
                    'id': fact.id,
                    'content': fact.content,
                    'image_url': fact.image_url,
                    'video_url': fact.video_url,
                    'status': fact.status,
                    'like_count': fact.like_count,
                    'dislike_count': fact.dislike_count,
                    'favorite_count': fact.favorite_count,
                    'created_at': fact.created_at.isoformat(),
                    'updated_at': fact.updated_at.isoformat()
                })
            
            return make_succ_response({
                'facts': facts_data,
                'pagination': {
                    'page': facts_pagination.page,
                    'pages': facts_pagination.pages,
                    'per_page': facts_pagination.per_page,
                    'total': facts_pagination.total,
                    'has_next': facts_pagination.has_next,
                    'has_prev': facts_pagination.has_prev
                }
            })
        else:
            return make_err_response('获取失败')
    except Exception as e:
        return make_err_response(f'获取失败: {str(e)}')