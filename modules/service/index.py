import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import init
from usr.index import UsrScript
import re
import pathlib
# [Apps]サービス・プロセス・アプリケーション情報取得用クラス
#
# ホスト上の稼働サービス・プロセスやインストールアプリケーションの情報等の処理を定義する。
#
# @access public
# @author - <-@->
# @copyright MIT
# @category サービス・プロセス・アプリケーション情報取得
# @package なし
class Apps:
    servicelist={}
    INTL={}
    def __init__(self, COMP_CONF):
        self.INTL=init.INTL

    # [Apps]サービス情報の取得
    #
    # サービスのリストを配列で返す。
    # $servicelist[all]に全サービスの情報を格納する。
    # $servicelist[static]に無効化されているサービスの情報を格納する。（[Install]セクションなし）
    # $servicelist[disabled]に無効化されているサービスの情報を格納する。（[Install]セクションあり）
    # $servicelist[enabled]に有効化されているサービスの情報を格納する。
    # $servicelist[running]に起動しているサービスの情報を格納する。
    # $servicelist[exited]に終了しているサービスの情報を格納する。
    # $servicelist[failed]に起動失敗しているサービスの情報を格納する。
    # $servicelist[dead]に停止しているサービスの情報を格納する。
    #
    # @access public
    # @param なし
    # @return array 導入サービスの一覧および状態
    # @see systemctl
    # @throws なし
    def GetService(self):
        usr=UsrScript()
        #servicelist={}
        servicelist={'all':[], 'static':[], 'enabled':[], 'disabled':[], 'running':[], 'exited':[], 'failed':[], 'dead': []}

        getServiceInfo=[
            {'command':"list-unit-files", 'state':['all', 'static', 'enabled', 'disabled']},
            {'command':"list-units", 'state':['running', 'exited', 'failed', 'dead']}
        ]

        for listdata in getServiceInfo:
            rc=usr.execUsrScript("systemctl", listdata['command'], "--type=service", "--no-legend")
            for val in rc['result']:
                if(rc['rcode'] != 0):
                    init.LAST_ERROR_MESSAGE=self.INTL.FormattedMessage("Fail_to_get_services_list")
                    return False

                tmp=re.sub('/\s+/', ' ', val)
                tmp=tmp.split(' ')

                tmp=list(filter(None, tmp))
                getUnit=''
                getState=''
                if(len(tmp) == 2):
                    getUnit, getState=tmp
                for state in listdata['state']:
                    if(getState == state or state=='all'):
                        #list(servicelist[state]).append({'unit':getUnit, 'state':getState})
                        servicelist[state].append({'unit':getUnit, 'state':getState})
        self.servicelist=servicelist
        return self.servicelist

    # [Apps]サービス登録有無の検索
    #
    # $serviceで指定するサービスが導入されているかどうかをboolで返す。
    # 未導入時、および導入情報取得失敗時はFALSEを返す。
    #
    # @access public
    # @param string $service 検索するサービス名
    # @return bool サービス導入有無
    # @see Apps->GetService
    # @throws なし
    def ServiceSearch(self, service):
        if(self.GetService() == False):
            return False
        for srvarr in self.servicelist['all']:
            if(service in srvarr):
                return True
        return False
    
    # [Apps]稼働プロセスの検索
    #
    # $processで指定するプロセスが稼働しているかどうかを稼働プロセス数で返す。
    # 未稼働時、またはプロセス情報取得失敗時はFALSEを返す。
    # プロセス情報は「modules/usr/bin/procnum.sh」で取得する。
    #
    # @access public
    # @param string $process 検索するプロセス名
    # @return int 稼働プロセス数
    # @see procnum.sh(ps aux | grep ${PROCNAME} | grep -v "\(root\|grep\)" | wc -l)
    # @throws なし
    def ProcessSearch(self, process):
        usr=UsrScript()

        #result['result'][0]=0
        #result['rcode']=False
        result={"result":[0]}
        result={'rcode':False}
        result=usr.execUsrScript(pathlib.Path(us.GetPathUsrBin()).joinpath("procnum.sh"), usr.GetPathUsrRoot(), process)
        if((not str.isnumeric(result['result'][0])) or (result['result'][0]==0) or (result['rcode'] != 0)):
            return False
        return int(result['result'][0])

    # [Apps]稼働サービスの検索
    #
    # $serviceで指定するサービスが稼働しているかどうかをboolで返す。
    # 稼働状況は$stateで示す文字列で指定する。$stateは("running"|"dead")を指定する。
    #  running：サービス稼働
    #  dead：サービス停止
    # 指定サービスがRunningの場合TRUEを返す。
    # 未稼働時、指定サービスが存在しない、およびサービス情報取得失敗時はFALSEを返す。
    #
    # @access public
    # @param string $service 検索するサービス名
    # @param string $state 検索するサービス状態
    # @return bool サービス稼働状況
    # @see systemctl
    # @throws なし
    def ServiceStatus(self, service, state="running"):
        if(not (state in ["running", "dead"])):
            init.LAST_ERROR_MESSAGE=self.INTL.FormattedMessage("Invalid_state", {'state':state})
            return False
        if(self.ServiceSearch(service) == False):
            init.LAST_ERROR_MESSAGE=self.INTL.FormattedMessage("Service_is_not_found", {'service':service})
            return False

        usr=UsrScript()
        serviceState=usr.execUsrScript("systemctl", "show", service, "--property=SubState")
        if(serviceState['rcode'] != 0):
            init.LAST_ERROR_MESSAGE=self.INTL.FormattedMessage("Fail_to_get_services_status", {'service':service})
            return False
        
        tmp=serviceState['result'][0]
        tmp=tmp.split('=')
        if(len(tmp) == 2):
            var, value=tmp
        return (value == state)

    # [Apps]停止サービスの検索
    #
    # $serviceで指定するサービスが停止しているかどうかをboolで返す。
    # 指定サービスがdeadの場合TRUEを返す。
    # 稼働時、failedの場合、およびサービス情報取得失敗時はFALSEを返す。
    #
    # @access public
    # @param string $service 検索するサービス名
    # @return bool サービス稼働状況
    # @see systemctl
    # @throws なし
    def ServiceStatusStopped(self, service):
        return self.ServiceStatus(service, "dead")

    # [Apps]サービスの起動
    #
    # $serviceで指定するサービスを起動する。
    # 指定サービスがRunningの場合、および起動成功時$trueを返す。
    # 指定サービスが存在しない場合、およびサービス起動失敗時は$falseを返す。
    #
    # @access public
    # @param string $service 起動するサービス名
    # @return bool サービス起動結果の状態
    # @see systemctl
    # @throws サービス起動で例外発生時、FALSEを返す。
    def ServiceStart(self, service):
        if(self.ServiceSearch(service) == False):
            init.LAST_ERROR_MESSAGE=self.INTL.FormattedMessage("Service_is_not_found", {'service':service})
            return False
        if(self.ServiceStatus(service) == True):
            return True
        if(self.ServiceCommand(service, "start") == False):
            init.LAST_ERROR_MESSAGE=self.INTL.FormattedMessage("Fail_to_start_service", {'service':service})
            return False

        return self.ServiceStatus(service)

    # [Apps]サービスの停止
    #
    # $serviceで指定するサービスを停止する。
    # 指定サービスがdeadの場合、および停止成功時TRUEを返す。
    # 指定サービスが存在しない場合、およびサービス停止失敗時はFALSEを返す。
    #
    # @access public
    # @param string $service 停止するサービス名
    # @return bool サービス停止結果の状態
    # @see systemctl
    # @throws サービス停止で例外発生時、FALSEを返す。
    def ServiceStop(self, service):
        if(self.ServiceSearch(service) == False):
            init.LAST_ERROR_MESSAGE=self.INTL.FormattedMessage("Service_is_not_found", {'service':service})
            return False
        if(self.ServiceStatusStopped(service) == True):
            return True
        if(self.ServiceCommand(service, "stop") == False):
            init.LAST_ERROR_MESSAGE=self.INTL.FormattedMessage("Fail_to_stop_service", {'service':service})
            return False
        return self.ServiceStatusStopped(service)

    # [Apps]サービスの操作
    #
    # $serviceで指定するサービスを起動・または停止する。$commandで操作する内容を指定する。
    # $commandは("start"|"stop")を指定する。
    #
    # @access private
    # @param string $service 操作するサービス名
    # @param string $command 操作する内容
    # @return bool サービス操作結果の状態
    # @see systemctl
    # @throws サービス操作で例外発生時、FALSEを返す。
    def ServiceCommand(self, service, command):
        if((command in ["start", "stop"]) == False):
            return False
        
        usr=UsrScript()
        serviceState=usr.execUsrScript("systemctl", command, service, "--no-ask-password")
        return (serviceState['rcode'] == 0)