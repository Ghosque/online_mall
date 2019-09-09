import pypinyin


# 不带声调的(style=pypinyin.NORMAL)
def chinese_to_pinyin(word):
    s = ''
    for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
        s += ''.join(i)

    return s
