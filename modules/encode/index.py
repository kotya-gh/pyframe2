# [Encode]文字のエンコード用クラス
#
# 文字のエンコード、デコードや変換のための処理を定義する。
#
# @access public
# @author - <-@->
# @copyright MIT
# @category 文字列エンコード
# @package なし
class Encode:

    def __init__(self):
        pass

    # [Encode]Jsonファイルを辞書に変換する
    #
    # file_pathで指定のファイルのJsonデコード結果を返す。
    #
    # @access private
    # @param pathlib file_path
    # @return dict decode_array ファイルのJsonデコード結果
    # @see 
    # @throws json.load、ファイルオープンで例外発生時、空の辞書を返す。
    def JsonFileDecode(self, path):
        import json
        try:
            rtn_json=json.load(open(str(path), 'r'))
        except json.JSONDecodeError as e:
            return {}
        except ValueError as e:
            return {}
        except Exception as e:
            return {}
        return rtn_json