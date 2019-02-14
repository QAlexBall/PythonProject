# -*- coding: utf-8 -*-
import asyncio
import functools
import inspect
import logging
import os
from urllib import parse

from aiohttp import web

from Python_lxf.awesomepython3webapp.www.apis import APIError


# 把一个函数映射为一个URL处理函数,先定义一个@get()
def get(path):
    """
    Define decorator @get('/path')
    @get装饰器,给处理函数绑定URL和HTTP method-GET属性
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)

        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper

    return decorator

# 定义一个@post()
def post(path):
    """
    Define decorator @post('/path')
    @post装饰器,给处理函数绑定URL和HTTP method-POST的属性
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)

        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper

    return decorator


def get_required_kw_args(fn):
    """ 将函数所有没有默认值的命名关键字参数名作为一个tuple返回 """
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
            args.append(name)
        return tuple(args)


def get_named_kw_args(fn):
    """ 将函数所有的命名关键字参数名作为一个tuple返回 """
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)


def has_named_kw_args(fn):
    """ 检查函数是否有命名关键字参数,返回布尔值 """
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True


def has_var_kw_arg(fn):
    """ 检查函数是否有关键字参数集,返回布尔值 """
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True


def has_request_arg(fn):
    """
    检查函数是否有request参数,返回布尔值.
    若有request参数,检查该参数是否为该函数的最后一个参数,否则抛出异常
    """
    sig = inspect.signature(fn)
    params = sig.parameters
    found = False
    for name, param in params.items():
        if name == 'request':
            found = True
            continue

        if found and (param.kind != inspect.Parameter.VAR_POSITIONAL and
                      param.kind != inspect.Parameter.KEYWORD_ONLY and
                      param.kind != inspect.Parameter.VAR_KEYWORD):
            raise ValueError('request parameter must be the last named parameter in function: %s%s' %
                             (fn.__name__, str(sig)))
    return found

class RequestHandler(object):
    """
    请求处理器,用来封装处理函数
    URL处理函数不一定是一个coroutine,用RequestHandler()来封装一个URL处理函数
    RequestHandler是一个类,由于定义了__call__()方法,因此可以将其实例视为一个函数
    RequestHandler目的就是从URL函数中分析其需要接收的参数,从request中获取必要的参数,调用URL函数,
    然后把结果转换为Web.Response对象,这样,就完全符合aiohttp框架的要求
    """

    def __init__(self, app, fn):
        # app: an application instance for registering the fn
        # fn: a request handler with a particular HTTP method and path
        self.app = app
        self._func = fn
        self._has_request_arg = has_request_arg(fn)
        self._has_var_kw_arg = has_var_kw_arg(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        self._named_kw_args = get_named_kw_args(fn)
        self._required_kw_args = get_required_kw_args(fn)

    async def __call__(self, request):
        """ 请求分析, request handler, must a coroutine that accepts a request instance
        as its only argument and returns a streamresponse derived instance """
        kw = None
        if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_args:
            # 当传入处理函数具有 关键字参数集 或 命名关键字参数 或 request参数
            if request.method == 'POST':
                # POST请求预处理
                if not request.content_type:
                    # 无正文类型信息时返回
                    return web.HTTPBadRequest('Missing Content-Type')
                ct = request.content_type.lower()
                if ct.startswith('application/json'):
                    # 处理函数JSON类型的数据,传入参数字典中
                    params = await request.json()
                    if not isinstance(params, dict):
                        return web.HTTPBadRequest('JSON body must be object.')
                    kw = params
                elif ct.startwith('application/x-www-form-urlencoded') or ct.startwith('multipart/form-data'):
                    # 处理表单类型的数据,传入参数字典中
                    params = await request.post()
                    kw = dict(**params)
                else:
                    # 暂不支持处理其他正文类型的数据
                    return web.HTTPBadRequest('Unsupported Content-Type: %s' % request.content_type)

            if request.method == 'GET':
                # get请求预处理
                qs = request.query_string
                # 获取URL中的请求参数,如name=JustOne, id=007
                if qs:
                    # 将请求参数传入参数字典中
                    kw = dict()
                    for k, v in parse.parse_qs(qs, True).items():
                        # parse a query string, data are returned as a dict. the dict keys are
                        # the unique query variable names and the values are lists of values for
                        # each name. a True value indicates that lanks should be retained as blank stirngs
                        kw[k] = v[0]
        if kw is None:
            # 请求无请求参数时
            kw = dict(**request.match_info)
            # Read-only property with AbstractMatchInfo instance for result of route resolving
        else:
            # 参数字典收集请求参数时
            if not self._has_named_kw_args and self._named_kw_args:
                copy = dict()
                for name in self._named_kw_args:
                    if name in kw:
                        copy[name] = kw[name]
                    kw = copy
                for k, v in request.match_info.items():
                    if k in kw:
                        logging.warning('Duplicate arg name in named arg and kw args: %s' % k)
                    kw[k] = v

        if self._has_request_arg:
            kw['request'] = request
        if self._required_kw_args:
            # 收集无默认的关键字参数
            for name in self._required_kw_args:
                if not name in kw:
                    # 当存在关键字参数未被赋值时返回,
                    # 例如 一般的账号注册时,没填入密码就提交注册申请时,提示密码未输入
                    return web.HTTPBadRequest('Missing arguments: %s' % name)
        logging.info('call with args: %s' % str(kw))
        try:
            r = await self._func(**kw)
            # 最后调用处理函数,并传入请求参数,进行请求处理
            return r
        except APIError as e:
            return dict(error=e.error, data=e.data, message=e.message)


def add_static(app):
    """添加静态资源路径"""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')  # 获取包含'static'的绝对路径
    # os.path.dirname(os.path.abspath(__file__)) 返回脚本所在目录的绝对路径
    app.router.add_static('/static/', path)  # 添加静态资源路径
    logging.info('add static %s => %s' % ('/static/', path))


def add_route(app, fn):
    """ 将处理函数注册到web服务程序的路由当中 """
    method = getattr(fn, '__method__', None)  # 获取 fn 的 __method__ 属性的值,无则为None
    path = getattr(fn, '__route__', None)  # 获取 fn 的 __route__ 属性的值,无则为None
    if path is None or method is None:
        raise ValueError('@get or @post not define in %s.' % str(fn))
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
        # 当处理函数不是协程时,封装为协程函数
        fn = asyncio.coroutine(fn)
    logging.info('add route %s %s => %s(%s)' % \
                 (method, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method, path, RequestHandler(app, fn))


def add_routes(app, module_name):
    """ 自动把handler模块符合条件的函数注册 """
    n = module_name.rfind('.')
    # rfind()返回字符串最后一次出现的位置
    if n == (-1):
        # 没有匹配时
        mod = __import__(module_name, globals(), locals())
        # print(mod)    <module 'handlers' from '/home/alex/WorkPlace/Python_Module/Python_lxf/awesomepython3webapp/www/handlers.py'>
        # import一个模块,获取模块名__name__
    else:
        # 添加模块属性 name,并赋值给mod
        name = module_name[n+1:]
        mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)
    for attr in dir(mod):
        # dir(mod)获取模块所有属性
        if attr.startswith('_'):
            # 略过所有私有属性
            continue
        fn = getattr(mod, attr)
        # 获取属性的值,可以是一个method
        if callable(fn):
            method = getattr(fn, '__method__', None)
            path = getattr(fn, '__route__', None)
            if method and path:
                # 对已经修饰过的URL处理函数注册到web服务的路由中
                add_route(app, fn)