import pathlib
import glob
import os
import sys
import re
import pwd
import socket
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import init
# [Log]テキストログの出力に関するクラス
#
# ログの出力を行うためのクラス。
#
# @access public
# @author - <-@->
# @copyright MIT
# @category システム操作
# @package なし
class Log:
    log_format={
        'message':'',
        'entry_type':'Error',
        'date':'',
        'source':'App1',
        'log_name':'Application',
        'event_id':65535,
        'username':'',
        'hostname':''
    }
    conf=[]
    INTL={}
    def __init__(self, COMP_CONF):
        self.conf=COMP_CONF

        self.log_format['username']=pwd.getpwuid(os.getuid())[0]
        self.log_format['hostname']=socket.gethostname()
        self.log_format['source']=self.conf['component_name']

        self.INTL=init.INTL

    # [Log]テキストログの書き込み
    #
    # ログをログファイルに書き込む。
    # ログ書き込み先のディレクトリが存在しない場合、コンポーネントと同名のディレクトリを作成する。作成失敗時はFALSEを返す。
    # ログは日付有りのファイル、および日付なしのファイルに同内容を書き込む。ログファイル名はコンポーネント名と同名となる。
    # ログ書き込み前にログローテート処理を行う。ログローテート失敗時はFALSEを返す。
    # ログ書き込み後、Log=>log_format['message']を空にする。
    #
    # @access public
    # @param なし
    # @return bool ログ書き込みの成否
    # @see MakeLogText(), LogRotation()
    # @throws ログ書き込みで例外発生時、FALSEを返す。
    def WriteLog(self):
        rc=True

        # ログ書き込みディレクトリの作成
        logDirPath=self.conf['path_log'].joinpath(self.conf['component_name'])        
        try:
            os.makedirs(logDirPath, exist_ok=True)
            os.chmod(logDirPath, 0o0770)
        except:
            init.LAST_ERROR_MESSAGE=self.INTL.FormattedMessage("Fail_to_make_log_directory")
            return False

        # 書き込み先ログファイルパスの作成
        rotateLogPath=logDirPath.joinpath(self.conf['component_name']+"_"+self.GetLogNameDate()+".log")
        currentLogPath=logDirPath.joinpath(self.conf['component_name']+".log")

        # ログローテート処理
        rotate=LogRotation()
        if(rotate.Rotate(rotateLogPath, currentLogPath, self.conf['log']['rotation']) == False):
            init.LAST_ERROR_MESSAGE=self.INTL.FormattedMessage("Fail_to_rotate_log")
            return False

        # ログ書き込み処理
        log_message=self.MakeLogText()
        if(log_message == False):
            init.LAST_ERROR_MESSAGE=self.INTL.FormattedMessage("Fail_to_make_log_text")
            return False

        # ログ書き込み後はメッセージ内容を空にする。
        try:
            f=open(rotateLogPath, 'a', encoding='UTF-8')
            f.write(log_message)
            f.close()
            f=open(currentLogPath, 'a', encoding='UTF-8')
            f.write(log_message)
            f.close()
        except:
            init.LAST_ERROR_MESSAGE=self.INTL.FormattedMessage("Fail_to_write_log")
            return False
        self.log_format['message']=""
        return True

    # [Log]ログフォーマットに則ったメッセージの作成
    #
    # 出力メッセージを整形する。
    # ログフォーマットに適合しない場合FALSEを返す。
    # Log->log_format['message']が空の場合はFALSEを返す。
    # Log->log_format['message']に改行が含まれる場合は改行を削除する。
    # 次のフォーマットでログテキストを作成する。
    # date <Application.INFORMATION> hostname username: [source="App1" eventid="65535"] message
    #
    # @access public
    # @param なし
    # @return bool ログメッセージ作成の成否
    # @see MakeLogTextPart(), GetFormattedDate()
    # @throws なし
    def MakeLogText(self):
        if(not self.log_format['message']):
            return False
        part=self.MakeLogTextPart()
        if(part == False):
            return False

        self.log_format['date']=self.GetFormattedDate()
        log_text=self.log_format['date']+' '+part+' '+ \
            self.log_format['message'].replace(os.linesep, ' ')+os.linesep
        return log_text

    # [Log]ログフォーマットに則ったメッセージの作成（日付、メッセージ以外）
    #
    # 出力メッセージを整形する。
    # ログフォーマットに適合しない場合FALSEを返す。
    # eventId、logName、entryTypeのバリデーションを実施し、適合しない場合はFALSEを返す。
    # 次のフォーマットでログテキストを作成する。
    # date <Application.INFORMATION> hostname username: [source="App1" eventid="65535"] message
    #
    # @access public
    # @param なし
    # @return bool ログメッセージ作成の成否
    # @see log_format['event_id'], log_format['log_name'], log_format['entry_type'], GetFormattedDate()
    # @throws なし
    def MakeLogTextPart(self):
        valid=LogValidation()
        if(
            (valid.eventId(self.log_format['event_id']) and
            valid.logName(self.log_format['log_name']) and
            valid.entryType(self.log_format['entry_type'])) == False
        ):
            return False
        self.log_format['date']=self.GetFormattedDate()
        log_text= \
            "<"+ \
            self.log_format['log_name']+"."+ \
            self.log_format['entry_type']+"> "+ \
            self.log_format['hostname']+" "+ \
            self.log_format['username']+': [source="'+ \
            self.log_format['source']+'" eventid="'+ \
            str(self.log_format['event_id'])+'"] '
        return log_text

    # [Log]ログ出力用日付情報の作成
    #
    # ログ出力用日付情報を返す。
    # 次のフォーマットで日時情報を作成する。
    # yyyy-MM-dd HH:mm:ss
    #
    # @access public
    # @param なし
    # @return string ログ出力用日付情報
    # @see format
    # @throws なし
    def GetFormattedDate(self):
        today = datetime.today()
        return format(today,'%Y-%m-%d %H:%M:%S')

    # [Log]ログファイル名用日付情報の作成
    #
    # ログファイル名用日付情報を返す。
    # 次のフォーマットで日付情報を作成する。
    # yyyymmdd
    #
    # @access public
    # @param なし
    # @return string ログファイル名用日付情報
    # @see format
    # @throws なし
    def GetLogNameDate(self):
        today = datetime.today()
        return format(today, '%Y%m%d')

# [LogRotation]テキストログのローテートに関するクラス
#
# ログのローテートを行うためのクラス。
#
# @access public
# @author - <-@->
# @copyright MIT
# @category システム操作
# @package なし
class LogRotation:
    def __init__(self):
        pass

    # [LogRotation]ログファイル名用日付情報の作成
    #
    # ログローテーション処理を実行する。
    # pathで示すファイルが存在しない場合（ログ書き込み時、当日の最初の書き込みである場合）、
    # ローテート対象であると判定し、カレントログの削除、指定世代以前の日付付きログファイルの削除を実施する。
    # ローテート対象ファイル削除失敗時はFALSEを返す。
    #
    # @access public
    # @param string path 日付付き最新ログファイルのフルパス
    # @param string currentPath カレントログファイルのフルパス
    # @param int rotation ローテート世代数
    # @return bool ローテートの成否
    # @see なし
    # @throws なし
    def Rotate(self, path, currentPath, rotation):
        if(pathlib.Path(path).exists() == True):
            return True

        # カレントログファイルの削除
        p=pathlib.Path(currentPath)
        if(p.exists() and p.unlink() == False):
            return False

        # 指定のローテーション以前の世代のファイルを削除
        d=os.path.dirname(path)
        filelist=glob.glob(os.path.join(d, '*.log'))
        list.sort(filelist, reverse=True)

        i=0
        for i, log in enumerate(filelist):
            if(re.match(r'^.*_\d{8}\.log$', log) ):
                i+=1
                p=pathlib.Path(log)
                if(i >= rotation):
                    if(p.unlink() == False):
                        return False
        return True

# [LogValidation]テキストログのバリデーションに関するクラス
#
# ログのバリデーションを行うためのクラス。
#
# @access public
# @author - <-@->
# @copyright MIT
# @category システム操作
# @package なし
class LogValidation:
    define_entry_type=["N/A", "Information", "Warning", "Error", "SuccessAudit", "FailureAudit"]
    define_all_log_name=["N/A", "Application", "System", "Security", "Setup"]
    define_max_event_id=65535

    def __init__(self):
        pass

    # [LogValidation]イベントIDのバリデーション
    #
    # eventIdが一定値以内であることを判定し、boolで返す。
    # eventIdは0以上LogValidation->define_max_event_id以下とする。
    # 適合しない場合はFALSEを返す。
    #
    # @access public
    # @param int eventId イベントID
    # @return bool バリデーションの結果
    # @see なし
    # @throws なし
    def eventId(self, eventId):
        return ((eventId >= 0) and (eventId <= self.define_max_event_id))

    # [LogValidation]ログネームのバリデーション
    #
    # logNameがLogValidation->define_all_log_nameに含まれていることを判定し、boolで返す。
    # 適合しない場合はFALSEを返す。
    #
    # @access public
    # @param int logName ログネーム
    # @return bool バリデーションの結果
    # @see なし
    # @throws なし
    def logName(self, logName):
        return (logName in self.define_all_log_name)

    # [LogValidation]エントリータイプのバリデーション
    #
    # entryTypeがLogValidation.define_entry_typeに含まれていることを判定し、boolで返す。
    # 適合しない場合はFALSEを返す。
    #
    # @access public
    # @param int entryType エントリータイプ
    # @return bool バリデーションの結果
    # @see なし
    # @throws なし
    def entryType(self, entryType):
        return (entryType in self.define_entry_type)