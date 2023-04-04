# [INIT]初期化処理用モジュール
#
# コンポーネント実行時Requireする。
# 共通ディレクトリの定義、設定読み込み、モジュール読み込みを実施する。
#
# @access public
# @author - <-@->
# @copyright MIT
# @category 初期化共通処理
# @package なし
import os
import sys
import json
import pathlib
import shutil
import hashlib

class Init:
    def __init__(self, self_path):

        # ルートディレクトリの定義
        self.__path_root=pathlib.Path(__file__).resolve().parents[1]
        
        # スクリプト構成ディレクトリの変数格納処理
        self.__path_conf=self.__path_root.joinpath('conf')
        self.__path_modules=self.__path_root.joinpath('modules')
        self.__path_log=self.__path_root.joinpath('log')
        self.__path_files=self.__path_root.joinpath('files')

        # スクリプトルートディレクトリの設定
        self.__path_script_root=pathlib.Path(self_path).parent

        # コンポーネント用外部ファイル名の格納
        self.__conflist_user=self.__path_script_root.glob('*.json')

        # スクリプト設定の格納
        self.__conf_require=self.__SetRequiredConfigure()
        
        # コンポーネント名の取得
        self.__component_name=self.__path_script_root.name

        # コンポーネントの設定ファイル名の格納
        self.__path_component_conf=self.__path_conf.joinpath(self.__component_name+'.json')

        # コンポーネントの設定内容の格納
        self.__conf_component=self.__SetComponentConfigure()

        # コンポーネント用外部ファイルのレプリケーション処理
        self.__ReplicationUserConfiture()

        # コンポーネント用外部ファイルの内容格納
        self.__conf_user=self.__SetUserConfiture()
        # パラメタ代入したほうがよい？ジェネレータが反映できない

        # モジュールの読み込み
        sys.path.append(str(self.__path_modules))

    def __GetComponentConfigure(self):
        return self.__conf_component

    def __GetComponentName(self):
        return self.__component_name

    def __GetFilesPath(self):
        return self.__path_files

    def __GetLogPath(self):
        return self.__path_log

    def __GetRequiredConfigure(self):
        return self.__conf_require

    def __GetModulesPath(self):
        return self.__path_modules

    def __GetUserConfigure(self):
        return self.__conf_user

    # [INIT]ファイルパスの作成
    # 
    # $dirで示すディレクトリと$fileで示すファイル名を結合してファイルパスを作成する。
    #
    # @access public
    # @param string $dir ディレクトリパス
    # @param string $file ファイル名
    # @return string フィアルパス
    # @see rtrim
    # @throws なし
    ### pythonのjoinpathを使用するため、メソッドは作成しない。

    # [INIT]ディレクトリパスの存在確認
    #
    # pathで指定するパスのディレクトリの存在を確認し、存在する場合は入力値、存在しない場合は作成後パスを返す。
    #
    # @access private
    # @param pathlib path ディレクトリパス
    # @return pathlib path ディレクトリパス
    # @see pathlib
    # @throws ディレクトリ作成失敗時はFalseを返す。
    def __GetExistDirPath(self, path):
        if(pathlib.Path(path).exists() == False):
            pathlib.Path(path).mkdir()
            if(pathlib.Path(path).is_dir() == False):
                return False
        return path

    # [INIT]ファイルパスの存在確認
    #
    # pathで指定するパスのファイルの存在を確認し、存在する場合は入力値、
    # 存在しない場合は空ファイルを作成後パスを返す。
    #
    # @access private
    # @param pathlib path ファイルパス
    # @return pathlib path ファイルパス
    # @see pathlib
    # @throws ファイル作成失敗時はFalseを返す。
    def __GetExistFilePath(self, path):
        if(pathlib.Path(path).exists() == False):
            pathlib.Path(path).touch()
            if(pathlib.Path(path).exists() == False):
                return False
        return path

    # [INIT]スクリプト全体設定ファイルの辞書変換
    #
    # スクリプト全体設定ファイル"require.json"を読み込み、Jsonデコード後の辞書を返す。
    #
    # @access private
    # @param なし
    # @return dict Jsonデコード後辞書
    # @see Init.__GetExistFilePath, Init.JsonFileDecode
    # @throws Init.JsonFileDecodeで例外発生時、$falseを返す。
    def __SetRequiredConfigure(self):
        path_conf_require=self.__GetExistFilePath(self.__path_conf.joinpath('require.json'))
        return self.__JsonFileDecode(path_conf_require)

    # [INIT]ユーザ設定ファイルのレプリケーション
    #
    # コンポーネントディレクトリ配下のJsonファイル（ユーザ設定ファイル）を、
    # コンポーネント設定ファイルで指定する場所からレプリケーションする。
    # コンポーネント設定ファイルのexecフラグが1の場合、かつ
    # レプリケーション元/先のファイルのハッシュ値が異なる場合レプリケーション処理を実行する。
    #
    # @access private
    # @param なし
    # @return bool レプリケーションの成否
    # @see pathlib, shutil, INIT.__Md5Sum
    # @throws ファイルコピーで例外発生時、Falseを返す。
    def __ReplicationUserConfiture(self):
        if(self.__conf_component['replication']['exec'] != 1):
            return True
        if(not(type(self.__conf_component['replication']['files']) is list)):
            return False
        for filepath in self.__conf_component['replication']['files']:
            if(
                (pathlib.Path(filepath).exists() == False) or
                (pathlib.Path(filepath).suffix != '.json')
            ):
                continue
            basename=pathlib.Path(filepath).name
            dstpath=self.__path_script_root.joinpath(basename)

            #ファイル名比較がフルパスになっていないので対応必要（PS,PHP）

            if((str(self.__path_script_root.joinpath(basename)) in self.__conflist_user) == False):
                try:
                    shutil.copy(filepath, str(dstpath))
                except Exception as e:
                    return False
            else:
                if(self.__Md5Sum(filepath) != self.__Md5Sum(dstpath)):
                    try:
                        shutil.copy(filepath, str(dstpath))
                    except Exception as e:
                        return False
        return True

    # [INIT]ファイルのチェックサム計算
    #
    # ファイルパス path を指定し、md5のチェックサムを返す。
    #
    # @access private
    # @param pathlib path ファイルパス
    # @return string hexdigest md5のチェックサム
    # @see hashlib
    # @throws なし
    def __Md5Sum(self, path):
        m=hashlib.md5()
        size=4096
        with open(str(path), 'rb') as f:
            for chunk in iter(lambda: f.read(size * m.block_size), b''):
                m.update(chunk)
        return m.hexdigest()

    # [INIT]ユーザ設定ファイルのJsonデコード
    #
    # コンポーネントディレクトリ配下のJsonファイル（ユーザ設定ファイル）をJsonデコードし、
    # ファイル名（拡張子なし）をキーとするハッシュに格納した結果を返す。
    #
    # @access public
    # @param なし
    # @return array $ret_hash ユーザ設定ファイルのJsonデコード結果
    # @see Init.JsonFileDecode
    # @throws Init.JsonFileDecodeで例外発生時、$falseを返す。
    def __SetUserConfiture(self):
        ret_hash={}
        for path_conf_user in self.__conflist_user:
            conf=path_conf_user.stem
            ret_hash[conf]=self.__JsonFileDecode(path_conf_user)
        return ret_hash

    # [INIT]コンポーネント設定ファイルのJsonデコード
    #
    # 共通設定ディレクトリ(conf)配下のJsonファイル（コンポーネント設定ファイル）を
    # Jsonデコードした結果を返す。
    # コンポーネントと同名の設定ファイルが存在しない場合、default.confのデコード結果を返す。
    #
    # @access private
    # @param pathlib Init.__path_component_conf
    # @return dict ret_hash ユーザ設定ファイルのJsonデコード結果
    # @see Init.__GetExistFilePath, Init.__JsonFileDecode
    # @throws Init.__JsonFileDecodeで例外発生時、空の辞書を返す。
    def __SetComponentConfigure(self):
        path=self.__path_component_conf if self.__path_component_conf.exists() else self.__path_conf.joinpath('default.json')
        return self.__JsonFileDecode(path)

    # [INIT]Jsonファイルを辞書に変換する
    #
    # file_pathで指定のファイルのJsonデコード結果を返す。
    #
    # @access private
    # @param pathlib file_path
    # @return dict decode_array ファイルのJsonデコード結果
    # @see 
    # @throws json.load、ファイルオープンで例外発生時、空の辞書を返す。
    def __JsonFileDecode(self, path):
        try:
            rtn_json=json.load(open(str(path), 'r'))
        except json.JSONDecodeError as e:
            return {}
        except ValueError as e:
            return {}
        except Exception as e:
            return {}
        return rtn_json

PROJECT_NAME="PyFrame 1.0"

# Version check >= 3
# Pythonバージョンの確認
version=sys.version_info.major
if(version < 3):
    print("Python(>=3.0) is required.")
    sys.exit(1)

# initクラスの初期化
INIT=Init(pathlib.Path(sys.argv[0]).resolve())

# include component configure
# 設定ファイルの読み込み、コンポーネント名、ログ格納ディレクトリの設定
COMP_CONF={'component_name':INIT._Init__GetComponentName(), 'path_log':INIT._Init__GetLogPath()}
tmp=INIT._Init__GetComponentConfigure()
len(tmp) == 0 or COMP_CONF.update(tmp)

# set user configuration
# ユーザ設定ファイルの読み込み
USR_CONF=INIT._Init__GetUserConfigure()

# set intl
# 出力メッセージ定義用処理の初期化
LOCALE=INIT._Init__GetRequiredConfigure()['locale']
from intl.index import Intl
INTL=Intl(os.path.join(os.path.dirname(pathlib.Path(sys.argv[0]).resolve()), 'locale'))

# set user log
from log.index import Log
USR_LOG=Log(COMP_CONF)
USR_MSG=USR_LOG.log_format

# コマンドライン引数
Args = sys.argv