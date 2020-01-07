# -*- coding: utf-8 -*-
import os
import oss2
import pymysql
from oss2.headers import OSS_OBJECT_TAGGING

update_sql = "UPDATE `{}` SET image='{}' WHERE id='{}'"
table = 'merchant_thirdcategory'

db = pymysql.connect(host="47.107.183.166", user="root", password="mysql", database="online_mall", charset="utf8")
cursor = db.cursor()
# 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录https://ram.console.aliyun.com创建RAM账号。
auth = oss2.Auth('LTAI4FwfrskcFinuqtNADg8Y', 'LrI2TbPEl467zC8qSgDpA87qIpDzsA')
# Endpoint以杭州为例，其它Region请按实际情况填写。
bucket = oss2.Bucket(auth, 'http://oss-cn-shenzhen.aliyuncs.com', 'ghosque-online-mall')

base_path = r'D:\Yang\Ghosque\online_mall\online_mall\online_mall\media\category\2'
for image in os.listdir(base_path):
    object_name = 'media/category/2/{}'.format(image)
    file_path = os.path.join(base_path, image)

    bucket.put_object_from_file(object_name, file_path)
    url = bucket.sign_url('GET', object_name, 5*12*30*24*60*60)

    id = image.split('.')[0]
    cursor.execute(update_sql.format(table, url, id))

db.commit()
db.close()
