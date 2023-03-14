import sys, os, pathlib, json, socket
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import init
from init import USR_CONF, INIT, INTL, USR_LOG, USR_MSG
from usr.index import UsrScript
from datetime import datetime

# エビデンス格納フォルダの作成
EvidenceHomeDir=""
if USR_CONF["list"]["EvidenceHomeDir"] == "":
    EvidenceHomeDir=INIT._Init__GetFilesPath().joinpath(INIT._Init__GetComponentName())
elif os.path.isdir(USR_CONF["list"]["EvidenceHomeDir"]) == False:
    EvidenceHomeDir=USR_CONF["list"]["EvidenceHomeDir"]
if os.path.isdir(EvidenceHomeDir) == False:
    os.makedirs(EvidenceHomeDir)

# ホスト名の取得
hostname=socket.gethostname()

# テストIDでループ
for testConfigure in USR_CONF["list"]["TestConfigure"]:
    # 格納フォルダの作成
    testIdDir=EvidenceHomeDir.joinpath(testConfigure["testId"])
    if os.path.isdir(testIdDir) == False:
        os.makedirs(testIdDir)

    # テスト開始メッセージ
    print(INTL.FormattedMessage("Starting_test_id", {"id":testConfigure["testId"]}))

    # テスト項目でループ
    for testItem in testConfigure["testItems"]:
        # 簡易チェック用変数
        CheckResult=True

        # エビデンス記録用データのオブジェクトを初期化
        testResult=[]

        # ホスト名が一致しない場合は処理をスキップ
        if hostname != testItem["hostname"]:
            continue

        # テスト用コマンドをオーダー順にソート
        # order属性でソートする関数
        def get_order(item):
            return item["order"]
        # 配列をソートして新しい配列を作る
        sortTestCommands = sorted(testItem["testCommands"], key=get_order)

        # テスト番号を0詰めで4桁表記とする
        testNo=str_num = "{:04d}".format(testItem["testNo"])

        # エビデンスを記録するテキストファイルとJSONファイルのパスを生成する無名関数
        def GenerateEvidenceFilePath(testNo, hostname, testIdDir):
            # datetimeモジュールをインポート
            from datetime import datetime
            # 現在の日付と時刻を取得
            now = datetime.now()
            # yyyyMMddHHmmss形式に変換
            startDateStr = now.strftime("%Y%m%d%H%M%S")
            # ファイル名を結合
            fileName=testNo+"_"+hostname+"_"+startDateStr
            # ファイルパスを返す
            return (testIdDir.joinpath(fileName))
        evidenceFileName=GenerateEvidenceFilePath(testNo, hostname, testIdDir)
        evidenceJsonFileName=GenerateEvidenceFilePath(testNo, hostname, testIdDir)

        # コマンド実行前メッセージ
        print(INTL.FormattedMessage("Starting_test_item_id", {"id":testNo, "hostname":hostname}))

        # テスト用コマンドを実行
        for command in sortTestCommands:
            # エビデンス記録用データのオブジェクトを初期化
            testResultObject={}

            def OutputMessage(message, filePath):
                print(message)
                with open(filePath, 'a') as f:
                    print(message, file=f)

            testResultObject["No"]=command["order"]

            # 実行コマンドの説明
            testResultObject["Command"]=command["command"]
            testResultObject["ExceptedResult"]=command["returnMsg"]
            testResultObject["ExceptedReturncode"]=command["returnCode"]
            OutputMessage(INTL.FormattedMessage("Running_command", {"command":command["command"]}), evidenceFileName)
            if command["returnMsg"] != "":
                OutputMessage(INTL.FormattedMessage("Command_result_message", {"returnMsg":command["returnMsg"]}), evidenceFileName)
            OutputMessage(INTL.FormattedMessage("Command_returncode", {"returncode":str(command["returnCode"])}), evidenceFileName)

            # コマンド実行時刻を取得
            now = datetime.now()
            startDate=now.strftime("%Y/%m/%d %H:%M:%S")
            OutputMessage(INTL.FormattedMessage("Start_datetime", {"datetime":startDate}), evidenceFileName)
            testResultObject["StartDatetime"]=startDate

            # コマンド実行
            execCommand=command["command"]
            usr = UsrScript()
            result=usr.execUsrScript(execCommand)

            # コマンド実行終了時刻を取得
            now = datetime.now()
            endDate=now.strftime("%Y/%m/%d %H:%M:%S")
            OutputMessage(INTL.FormattedMessage("End_datetime", {"datetime":endDate}), evidenceFileName)
            testResultObject["StopDatetime"]=startDate

            # コマンド実行結果を出力
            OutputMessage(INTL.FormattedMessage("Command_result"), evidenceFileName)
            resultOutputString = "\n".join(result["result"])
            testResultObject["CommandResult"]=resultOutputString
            OutputMessage(resultOutputString, evidenceFileName)

            OutputMessage(INTL.FormattedMessage("Command_return_code", {"returncode":str(result["rcode"])}), evidenceFileName)
            testResultObject["Returncode"]=result["rcode"]

            # 簡易チェック
            tmpResult=(result["rcode"] == command["returnCode"]) and ((command["returnMsg"] == "") or ((command["returnMsg"] in resultOutputString) != False))
            if tmpResult == False:
                CheckResult=tmpResult
            testResultObject["CheckResult"]=tmpResult

            # 改行
            OutputMessage("\n", evidenceFileName)
            testResult.append(testResultObject)

        suffix = "_true" if CheckResult else "_false"
        evidenceFileName.rename(str(evidenceFileName)+suffix+".txt")
        evidenceJsonFileName = pathlib.Path(str(evidenceJsonFileName)+suffix+".json")
        with open(evidenceJsonFileName, 'a') as f:
           json.dump(testResult, f)