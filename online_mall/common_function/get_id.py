import datetime
import random
import string
from random import shuffle


class GetId:

    # 获取唯一标识
    @classmethod
    def getId(cls):
        # 只要秒数大于60466175，就可以转换出6位的36进制数，这里从2015年1月1日开始计算，约70年后会变成7位
        d1 = datetime.datetime(2015, 1, 1)
        d2 = datetime.datetime.now()
        # 获取秒数
        s = (d2 - d1).days * 24 * 60 * 60
        # 获取微秒数
        ms = d2.microsecond
        # 随机两位字符串
        id1 = cls.hex36(random.randint(36, 1295))
        # 转换秒数
        id2 = cls.hex36(s)
        # 转换微秒数，加46656是为了保证达到4位36进制数
        id3 = cls.hex36(ms + 46656)

        mId = id1 + id2 + id3
        str_list = list(mId)
        shuffle(str_list)
        return ''.join(str_list)

    @staticmethod
    def hex36(num):
        # 正常36进制字符应为'0123456789abcdefghijklmnopqrstuvwxyz'，这里我打乱了顺序
        key = 't5hrwop6ksq9mvfx8g3c4dzu01n72yeabijl'
        key_list = list(key)
        shuffle(key_list)
        key = ''.join(key_list)
        a = []
        while num != 0:
            a.append(key[num % 36])
            num //= 36
        a.reverse()
        out = ''.join(a)
        return out

    @classmethod
    def getDigitId(cls):
        return ''.join(random.sample(string.digits, 6))

    @classmethod
    def getOrderId(cls):
        return ''.join(random.choice(string.digits) for i in range(15))
