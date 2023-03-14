import os
import pathlib
import glob
import subprocess
from str.index import Str
# [UsrScript]ユーザ作成スクリプト実行用クラス
#
# ユーザ作成スクリプトを実行するための処理、格納場所を定義する。
#
# @access public
# @author - <-@->
# @copyright MIT
# @category ユーザスクリプト実行処理
# @package なし
class UsrScript:
    path_usr_root=""
    path_usr_bin=""
    scriptList=[]

    def __init__(self):
        self.path_usr_root=os.path.dirname(__file__)
        self.path_usr_bin=self.GetExistDirPath(pathlib.Path(self.path_usr_root).joinpath('bin'))
        self.scriptList=glob.glob(os.path.join(self.path_usr_bin, '*'))

    def GetScriptList(self):
        return self.scriptList
    def GetPathUsrRoot(self):
        return self.path_usr_root
    def GetPathUsrBin(self):
        return self.path_usr_bin

    # [UsrScript]ディレクトリパスの存在確認
    #
    # $pathで指定するパスのディレクトリの存在を確認し、存在する場合は入力値、存在しない場合は作成後パスを返す。
    #
    # @access private
    # @param string $path ディレクトリパス
    # @return string $path ディレクトリパス
    # @see mkdir
    # @throws なし
    def GetExistDirPath(self, path):
        if(pathlib.Path(path).exists() != True):
            try:
                os.makedirs(path, exist_ok=True)
                os.chmod(path, 0o0770)
            except:
                return False
        return path

    # [UsrScript]ユーザ作成スクリプトの実行
    # 
    # $commandで指定するコマンドを実行し、実行結果と終了コードをハッシュで返す。
    # コマンドのオプションは$argsで指定する。
    #
    # @access public
    # @param string $command コマンド名
    # @param string ...$args コマンドオプション（可変長）
    # @return array result=>コマンド結果:array, 'rcode'=>終了コード:int
    # @see exec, escapeshellcmd, escapeshellarg
    # @throws なし
    def execUsrScript(self, command, *args):
        args=list(args)
        cmdline=[]
        #cmdline.append(command)
        cmdline.extend(command.split())
        if args:
            cmdline.extend(args)
        stdout=""
        stderr=""
        cp = subprocess.run(cmdline, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        st=Str()
        return {'result':st.clearListWhiteSpaceElement(cp.stdout.splitlines()), 'rcode':cp.returncode, 'stderr':stderr}