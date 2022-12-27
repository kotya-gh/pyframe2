import re
# [Str]文字列処理用クラス
#
# 文字列を加工する処理を定義する。
#
# @access public
# @author - <-@->
# @copyright MIT
# @category 文字列処理
# @package なし
class Str:
    def __init__(self):
        pass

    def clearWhiteSpace(self, string):
        return re.sub('/\s+/', '', string)
        # defineWhiteChars=[" ", "\n", "\t", "\v", "\f", "\r"]
        # for char in defineWhiteChars:
        #     string=string.replace(char,"")
        # return string

    def clearListWhiteSpaceElement(self, listdata):
        for i, val in enumerate(listdata):
            if(self.clearWhiteSpace(val) == ""):
                listdata[i]=self.clearWhiteSpace(val)
        return list(filter(None, listdata))
