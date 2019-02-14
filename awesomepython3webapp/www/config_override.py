"""
如果要部署到服务器时,通常需要修改数据库的host等信息,编写一个config_override.py,用来覆盖某些默认设置
"""
# config_override.py

configs = {
    'db': {
        'host': '127.0.0.1'
    }
}

