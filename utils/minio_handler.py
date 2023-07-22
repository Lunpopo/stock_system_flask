import traceback

import minio
from gkestor_common_logger import Logger


logger = Logger()

MINIO_BUCKET_POLICY = """
{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {
            "AWS": ["*"]
        },
        "Action": ["s3:GetBucketLocation", "s3:ListBucket", "s3:ListBucketMultipartUploads"],
        "Resource": ["arn:aws:s3:::%s"]
    }, {
        "Effect": "Allow",
        "Principal": {
            "AWS": ["*"]
        },
        "Action": ["s3:ListBucket"],
        "Resource": ["arn:aws:s3:::%s"],
        "Condition": {
            "StringEquals": {
                "s3:prefix": ["*"]
            }
        }
    }, {
        "Effect": "Allow",
        "Principal": {
            "AWS": ["*"]
        },
        "Action": ["s3:ListMultipartUploadParts", "s3:PutObject", "s3:AbortMultipartUpload", "s3:DeleteObject", "s3:GetObject"],
        "Resource": ["arn:aws:s3:::%s/*"]
    }]
}"""


class MinioHandler:
    """
    Minio处理器
    """

    def __init__(self, host, access_key, secret_key, secure=False):
        self.host = host
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        self.minio_client = None

    def test_connection(self):
        """
        测试连接
        :return:
        """
        if not self.minio_client:
            self.minio_client = minio.Minio(self.host, access_key=self.access_key, secret_key=self.secret_key,
                                            secure=self.secure)

        try:
            self.minio_client.list_buckets()
            return True
        except Exception:
            return False

    def get_connection(self):
        """
        获取 minio 实例对象
        :return:
        """
        if not self.minio_client:
            self.minio_client = minio.Minio(self.host, access_key=self.access_key, secret_key=self.secret_key,
                                            secure=self.secure)

        return self.minio_client

    def fget(self, bucket_name, object_name, file_path="./img.tif"):
        """
        下载文件
        :param bucket_name:
        :param object_name:
        :param file_path:
        :return:
        """
        self.minio_client.fget_object(
            bucket_name=bucket_name,
            object_name=object_name,
            file_path=file_path
        )
        return file_path

    def fput_object(self, minio_object_filepath, local_file, bucket_name=''):
        """
        文件上传到对象中，例如：simple-etl-python, leading-data/1.txt, 1.txt

        :param minio_object_filepath: structured-data/waijun-system/wjsj.zip
        :param local_file: wjsj.zip
        :param bucket_name: simple-etl-python-test
        :return: file_info_dict
        """
        if not self.minio_client:
            self.minio_client = self.get_connection()

        if not self.minio_client.bucket_exists(bucket_name=bucket_name):
            self.minio_client.make_bucket(bucket_name=bucket_name)
        upload_location = None
        file_info_dict = {
            "upload_location": upload_location,
            "bucket_name": None,
            "object_name": None
        }

        # 设置存储桶的权限
        policy = MINIO_BUCKET_POLICY % (bucket_name, bucket_name, bucket_name)
        self.minio_client.set_bucket_policy(bucket_name=bucket_name, policy=policy)

        try:
            # 直接上传覆盖原文件
            minio_file_object = self.minio_client.fput_object(bucket_name, minio_object_filepath, local_file)
            if minio_file_object.location:
                upload_location = minio_file_object.location
            else:
                upload_location = "/".join(["http:/", self.host, minio_file_object.bucket_name,
                                            minio_file_object.object_name])

            file_info_dict["upload_location"] = upload_location
            file_info_dict['bucket_name'] = bucket_name
            file_info_dict['object_name'] = minio_file_object.object_name
        except:
            logger.error("上传到minio的过程中出错了，详细的信息如下：")
            logger.error(traceback.format_exc())
            return file_info_dict

        return file_info_dict

    def remove_object(self, bucket_name, object_name):
        """
        删除 minio 文件
        :param bucket_name:
        :param object_name:
        :return:
        """
        if not self.minio_client:
            self.minio_client = self.get_connection()
        try:
            self.minio_client.remove_object(bucket_name=bucket_name, object_name=object_name)
        except:
            return False

        return True
