# [Calc]計算用クラス
#
# 各種の計算、単位変換処理を定義する。
#
# @access public
# @author - <-@->
# @copyright MIT
# @category 計算処理
# @package なし
class Calc:
    __units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB")
    def __init__(self):
        pass

    # [Calc]単位付き数字の変換
    #
    # sizeで指定する数値＋単位（1,024KB、25GB、100TBなど）の文字列を、unitで指定の単位に変換した結果をlistで返す。
    # listは、(数値,単位文字列)で返す。
    # 使用可能な単位は、("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB")とする。
    # 単位の繰り上がり数はcarrysizeで指定する。指定しない場合、1024を使用する。
    # 変換失敗時、listで(False,False)を返す。
    #
    # @access public
    # @param string size 数値＋単位の文字列
    # @param string unit 変換後の単位
    # @param int carrysize 単位の繰り上がり数（デフォルト値は1024）
    # @return list (数値, 単位文字列)
    # @see math.round
    # @throws sizeのフォーマット不正時、およびunitの文字列が不正時、Falseとする。
    def UnitConversion(self, size, unit, carrysize=1024):
        if(((unit in self.__units) == False) or (isinstance(carrysize, int) == False)):
            return False, False
        import math
        try:
            src_size, src_unit=self.GetSizeAndUnit(size)
        except:
            return False, False

        i = self.__units.index(unit.upper())
        j = self.__units.index(src_unit.upper())
        dst_size = round(src_size / carrysize ** (i-j), 2)

        return dst_size, unit

    # [Calc]単位付き数字の分割
    #
    # sizeで指定する数値＋単位（1,024KB、25GB、100TBなど）の文字列を、数値と単位に分割し、listで返す。
    # listは、(数値,単位文字列)で返す。
    # 使用可能な単位は、("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB")とする。
    # 分割失敗時、listで(False,False)を返す。
    #
    # @access public
    # @param string size 数値＋単位の文字列
    # @return list (数値, 単位文字列)
    # @see math.round
    # @throws sizeのフォーマット不正時、およびunitの文字列が不正時、Falseとする。
    def GetSizeAndUnit(self, size):
        import re
        numarr=re.split('[A-z]+', size)
        unit=size[len(numarr[0]):]
        try:
            num=float(numarr[0].replace(',', ''))
        except:
            return False, False

        if(unit in self.__units):
            return num, unit
        return False, False

