#!/bin/bash
##
# [common]共通処理用ライブラリ
#
# bashスクリプトの共通処理を定義する。
#
# @access public
# @author - <-@->
# @copyright MIT
# @category 共通処理
# @package なし
#

# リターンコード
NORMAL_END=0
INVALID_PARAMETER_ERR=10
FAIL_TO_DECODE_PASSWORD=11
SRV_CONNECT_ERR=20
FILE_NOT_EXIST_ERR=30
FILE_IMPORT_ERR=31

# 日時編集
DATE=`date "+%Y%m%d"`
DATETIME=`date "+%Y%m%d_%H%M%S"`

# ホスト名
SERVERNAME=`uname -n`

# スクリプト格納ディレクトリ
HOMEDIR=`dirname "$0"`

# スクリプト名
SCRIPT_NAME=$(basename "$0")

# スクリプト名(拡張子なし)
export SCRIPT=`basename -s .sh ${SCRIPT_NAME}`

# 実行ファイル格納ディレクトリ
BIN_PATH="${ROOT_PATH}"/bin/

# ライブラリファイル格納ディレクトリ
LIB_PATH="${ROOT_PATH}"/lib/

# 環境変数ファイル格納ディレクトリ
ENV_PATH="${ROOT_PATH}"/etc/

# スクリプトログファイル格納ディレクトリ
LOG_PATH="${ROOT_PATH}"/log/

# 実行ログ
export LOGFILE=${LOG_PATH}${DATE}_${SERVERNAME}_${SCRIPT}.log

# 環境変数読み込み
. "${ENV_PATH}""common.env"

##
# [common]ローカルログ出力関数
# 
# 引数の内容を標準出力とローカルログへ出力する。
# 
# @access public
# @param string MSGTXT ログ出力メッセージ
# @return なし
# @see なし
# @throws なし
#
OUTPUT_LOCAL_LOG ()
{
	# 日時編集
	MSGOUT_DATETIME=`date "+%Y-%m-%d %H:%M:%S"`

	# 標準出力と実行ログへメッセージを出力
	MSGTXT=$*
	echo "${MSGOUT_DATETIME} ${MSGTXT}" 2>&1 | tee -a ${LOGFILE}
}

##
# [common]システムログ出力関数
# 
# 引数の内容を標準出力、ローカルログ、システムログへ出力する。
# システムログにはプライオリティ「error」で出力する。
# 
# @access public
# @param string MSGTXT ログ出力メッセージ
# @return なし
# @see なし
# @throws なし
#
OUTPUT_SYSLOG ()
{
	# 標準出力と実行ログへメッセージを出力
	MSGTXT=$*
	OUTPUT_LOCAL_LOG ${MSGTXT}

	# システムログへメッセージを出力
	logger -p user.err -t ${SCRIPT} "[error] ${MSGTXT}"
}

##
# [common]コールスタック
# 
# このファイルを呼び出し元のファイル名を取得する。
# 
# @access public
# @param なし
# @return 呼び出し元のファイル名
# @see なし
# @throws なし
#
TRACE_PARENTS()
{
	local pid=$$ cmd
	while true; do
		cmd="$(cat /proc/$pid/cmdline | tr '\0' ' ')"
		echo -e "pid=$pid, cmd=$cmd"
		[ $pid -eq 1 ] && break
		pid=$(awk '/^PPid:/{print $2}' /proc/$pid/status)
	done
}

##
# [common]終了処理関数
# 
# MSGTXTで示す文字列をローカルログに出力し、EXIT_CDで示す終了コードでスクリプトを終了する。
# 
# @access public
# @param int EXIT_CD 終了コード
# @param string MSGTXT ログ出力メッセージ
# @return int EXIT_CD 終了コード
# @see なし
# @throws なし
#
EXIT_FUNC ()
{
	# 引数取得
	EXIT_CD=$1		# 終了コード
	MSGTXT=${@:2}	# メッセージ

	# 処理終了メッセージ出力
	OUTPUT_LOCAL_LOG "${MSGTXT}"

	exit ${EXIT_CD}
}

##
# [common]ライブラリ読み込み関数
# 
# LIB_FILEで指定するファイル名のライブラリをインポートする。
# 指定するライブラリが存在しない場合、終了コード「FILE_NOT_EXIST_ERR」でスクリプトを終了する。
# 
# @access public
# @param string LIB_FILE 読み込むライブラリファイル名（basenameのみを指定する）
# @return int EXIT_CD 終了コード
# @see なし
# @throws なし
#
COMMON_MSG005001='ライブラリファイルの読み込みに失敗しました。処理を終了します。'

INCLUDE (){
	LIB_FILE=$1

	if [ -r ${LIB_PATH}${LIB_FILE} ]
	then
		. ${LIB_PATH}${LIB_FILE}
	else
		# 存在確認エラーメッセージ出力
		echo "${COMMON_MSG005001}"
		exit ${FILE_NOT_EXIST_ERR}
	fi
}