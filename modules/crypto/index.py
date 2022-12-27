from usr.index import UsrScript
import pathlib
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import init
# [Crypt]暗号化処理用クラス
#
# 文字列、ファイルの暗号化処理を定義する。
#
# @access public
# @author - <-@->
# @copyright MIT
# @category 暗号化処理
# @package なし
class Crypt:
    def __init__(self):
        pass

    # [Crypt]文字列のAES 256暗号化
    #
    # $dataで指定する文字列をAES 256で暗号化した文字列を返す。
    # $passwordでパスワード文字列を指定する。
    #
    # @access public
    # @param string $data 平文
    # @param string $password パスワード
    # @return string 暗号化文字列(base64)
    # @see openssl_encrypt
    # @throws なし
    def encrypt(self, data, password):
        us=UsrScript()
        res=us.execUsrScript( \
            "bash", \
            pathlib.Path(us.GetPathUsrBin()).joinpath("encrypt.sh"), \
            us.GetPathUsrRoot(), \
            data, \
            password)

        if(res["rcode"] != 0):
            init.LAST_ERROR_MESSAGE=res["stderr"]
            return False
        return res["result"][0]
    
    # [Crypt]AES 256で文字列の復号
    #
    # $edataで指定する文字列をAES 256で復号した文字列を返す。
    # $passwordでパスワード文字列を指定する。
    #
    # @access public
    # @param string $edata 暗号化文字列(base64)
    # @param string $password パスワード
    # @return string 復号文字列
    # @see openssl_decrypt
    # @throws なし
    def decrypt(self, data, password):
        us=UsrScript()
        res=us.execUsrScript( \
            "bash", \
            pathlib.Path(us.GetPathUsrBin()).joinpath("decrypt.sh"), \
            us.GetPathUsrRoot(), \
            data, \
            password)

        if(res["rcode"] != 0):
            init.LAST_ERROR_MESSAGE=res["stderr"]
            return False
        return res["result"][0]