#  [Intl]言語設定用クラス
#
#  多言語対応用の処理を定義する。
#
#  @access public
#  @author - <-@->
#  @copyright MIT
#  @category 多言語用処理
#  @package なし
import sys
import os
import pathlib
from encode.index import Encode

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import init

class Intl():
    __path=""
    __define={}

    def __init__(self, path):
        define=os.path.join(os.path.dirname(__file__), 'define.json')        
        en=Encode()
        self.__define=en.JsonFileDecode(define)

        # init lang
        self.__path=os.path.join(path, self.defaultLocale(init.LOCALE)+".json")
    
    # [Intl]ロケール文字列の取得
    #
    # $localeで指定するロケール名が定義されている場合、入力値を返す。
    # 定義されていないロケールの場合"ja_JP"を返す。
    #
    # @access private
    # @param string $locale ロケール文字列
    # @return string ロケール文字列
    # @see
    # @throws なし
    def defaultLocale(self, locale):
        if((locale in self.__define['lang']) == True):
            return locale
        return "ja_JP"
    
    # [Intl]IDから文字列を取得
    #
    # $idで指定するIDに対応する文字列を返す。
    # 文字列内に$valueのハッシュキーを「__(ハッシュキー)」の形式で記載している場合、対応するハッシュ値と入れ替える。
    # 存在しない$idを指定した場合、$falseを返す。
    #
    # @access public
    # @param string $id 検索用ID
    # @param object $value メッセージ内文字列変換用ハッシュ
    # @return string $returnString IDに対応する文字列
    # @see Get-Content
    # @throws メッセージ定義ファイル取得で例外発生時、$falseを返す。
    def FormattedMessage(self, id, values={}):
        if(pathlib.Path(self.__path).exists() == False):
            init.LAST_ERROR_MESSAGE="No lang file.("+self.__path+")"
            return False
        # import lang file.
        en=Encode()
        lang=en.JsonFileDecode(self.__path)
        # search lang key
        if((id in lang)==False):
            init.LAST_ERROR_MESSAGE="No id is found.("+id+")"
            return False
        returnString=lang[id]
        for key, value in values.items():
            returnString=returnString.replace('__('+key+')', value)
        return returnString