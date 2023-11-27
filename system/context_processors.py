# 在 context_processors.py 文件中

def user_info(request):
    # 从会话中获取用户名
    username = request.session.get('username', None)

    return {'username': username}
