"""
应用程序读取配置文件优先从config_override.py读取.
为了简化读取配置文件,可以把所有配置读取到统一的config.py中.
"""

from Python_lxf.awesomepython3webapp.www import config_default


class Dict(dict):
    """
    Simple dict but support access as x.y style.
    """

    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value


def merge(defaults, override):
    r = {}
    for k, v in defaults.items():
        if k in override:
            if isinstance(v, dict):
                r[k] = merge(v, override[k])
            else:
                r[k] = override[k]
        else:
            r[k] = v
    return r


def toDict(d):
    D = Dict()
    for k, v in d.items():
        D[k] = toDict(v) if isinstance(v, dict) else v
    return D


configs = config_default.configs

try:
    from Python_lxf.awesomepython3webapp.www import config_override

    configs = merge(configs, config_override.configs)
except ImportError:
    pass

configs = toDict(configs)
print(configs)

# a = Dict(('a', 'b'), (0, 1, 3))
# print(a)
# print(a.a, ' ', a.b)  # __getattr__ return self[key] = value
# print(a.c) __getattr__ except KeyError
