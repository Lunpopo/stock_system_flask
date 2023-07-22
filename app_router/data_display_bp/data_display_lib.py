import os
import time
import urllib

from PIL import Image
from gkestor_common_logger import Logger

from configs.contents import TEMP_DIR, MINIO_HOSTS, ACCESS_KEY, SECRET_KEY
from utils.date_utils import time_to_timestamp
from utils.minio_handler import MinioHandler

logger = Logger()
minio_handler = MinioHandler(host=MINIO_HOSTS, access_key=ACCESS_KEY, secret_key=SECRET_KEY)
minio_handler.get_connection()


def format_dealer_product(data_list):
    """
    处理搜索经销商产品数据的方法，将返回的 tuple 结果进行格式化json
    :param data_list: 接收搜索返回的数据（tuple类型，第一列是 DealerProductList 数据类型，第二列是 ProductList 数据类型）
    :return:
    """
    return_data_list = []
    for dealer_product_obj, product_obj in data_list:
        # json格式化
        dealer_product_dict = dealer_product_obj.as_dict()
        # 添加几个列名
        dealer_product_dict['product_name'] = product_obj.product_name
        dealer_product_dict['specifications'] = product_obj.specifications
        dealer_product_dict['scent_type'] = product_obj.scent_type
        dealer_product_dict['specification_of_piece'] = product_obj.specification_of_piece
        dealer_product_dict['img_url'] = product_obj.img_url
        dealer_product_dict['thumb_img_url'] = product_obj.thumb_img_url
        return_data_list.append(dealer_product_dict)

    # 统一转换成时间戳的形式
    return time_to_timestamp(return_data_list)


def upload_image_thumb(file_obj, product_name, dealer_name='myself'):
    """
    上传 img 图片 和 缩略图到 minio 中
    :param file_obj: 前端传过来的 data 文件对象
    :param product_name: 产品名称
    :param dealer_name: 经销商名称，默认是 myself
    :return:
    """
    # 后端加一个验证，是否为 png 或 jpg 图片
    filename = file_obj.filename
    # 文件的后缀
    file_ext = filename.split(".")[-1]
    if file_ext != "jpg" and file_ext != "jpeg" and file_ext != "png":
        logger.info("更新 {} 产品 出错，不能处理的图像类型！".format(product_name))
        raise Exception("不能处理的图像类型：{}".format(file_ext))

    current_dealer_dir = os.path.join(TEMP_DIR, dealer_name)
    current_dealer_img_dir = os.path.join(current_dealer_dir, "images")
    current_dealer_thumb_dir = os.path.join(current_dealer_dir, "thumb")

    filename = "{}.png".format(product_name)

    if not os.path.exists(TEMP_DIR):
        os.mkdir(TEMP_DIR)
    if not os.path.exists(current_dealer_dir):
        os.mkdir(current_dealer_dir)
    if not os.path.exists(current_dealer_img_dir):
        os.mkdir(current_dealer_img_dir)
    if not os.path.exists(current_dealer_thumb_dir):
        os.mkdir(current_dealer_thumb_dir)
    file_path = os.path.join(current_dealer_img_dir, filename)
    # 保存图片文件到 tmp 目录
    file_obj.save(file_path)

    # 通过Image对象的thumbnail方法生成指定尺寸的缩略图
    image = Image.open(file_path)
    image.thumbnail((256, 256))
    thumb_filename = "{}_thumb.png".format(filename.split(".")[0])
    thumb_filepath = os.path.join(current_dealer_thumb_dir, thumb_filename)
    image.save(thumb_filepath)

    # 上传图片到minio，获取返回地址
    upload_object_name = os.path.join("{}/images".format(dealer_name), filename)
    upload_object_name = urllib.parse.unquote(upload_object_name, 'utf-8')
    upload_thumb_object_name = os.path.join("{}/thumb".format(dealer_name), thumb_filename)
    upload_thumb_object_name = urllib.parse.unquote(upload_thumb_object_name, 'utf-8')
    minio_image_dict = minio_handler.fput_object(
        minio_object_filepath=upload_object_name, local_file=file_path, bucket_name="order-system"
    )
    minio_thumb_dict = minio_handler.fput_object(
        minio_object_filepath=upload_thumb_object_name, local_file=thumb_filepath, bucket_name="order-system"
    )

    image_url = minio_image_dict.get('upload_location')
    thumb_url = minio_thumb_dict.get('upload_location')
    if '%' in image_url:
        pass
    return {
        "img_url": "{}?{}".format(image_url, int(time.time())),
        "thumb_img_url": "{}?{}".format(thumb_url, int(time.time()))
    }
