def singleton(cls):
    # 采用字典，可以装饰多个类，控制多个类实现单例模式
    _instance_dict = {}

    def inner(*args, **kwargs):
        if cls not in _instance_dict:
            _instance_dict[cls] = cls(*args, **kwargs)
        return _instance_dict.get(cls)

    return inner
