def time_to_timestamp(data_list):
    """
    将datetime类型转换为时间戳
    :param data_list:
    :return:
    """
    if data_list:
        for _ in data_list:
            # 转换没有指定时区
            _['create_time'] = int(_.get('create_time').timestamp())
            _['update_time'] = int(_.get('update_time').timestamp())
        return data_list
    else:
        return []
