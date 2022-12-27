#!/bin/bash
##
# [remoteExec]リモートコマンド実行処理
# 
# sshでリモート接続し、コマンドを実行する。実行結果を標準出力で表示する。
# パスフレーズはbase64エンコードした文字列を指定する。
# SSH_ACCESS成功時は終了コード0で終了する。
# 
# @access public
# @param string $1 ROOTパス
# @param string $2 接続先サーバホスト名（IPアドレス）
# @param string $3 サーバユーザ名
# @param string $4 パスフレーズ
# @param string $5 リモートコマンド（可変長）
# @return SSH_ACCESS処理終了コード
# @see lib_ssh.sh->SSH_ACCESS
# @throws なし
#
#----------------------------------------
# 初期設定
#----------------------------------------
if [ $# -le 4 ]; then
	echo "パラメタが不足しています。"${SCRIPT_NAME}"の処理を終了します。"
    exit ${INVALID_PARAMETER_ERR} 
fi

# ROOTパス
ROOT_PATH=$1

#----------------------------------------
# 初期処理
#----------------------------------------
if [ -r "${ROOT_PATH}"/etc/common.sh ]
then
	. "${ROOT_PATH}"/etc/common.sh
else
	# 存在確認エラーメッセージ出力
	echo "共通処理ファイルの読み込みに失敗しました。処理を終了します。"
	exit 31
fi

#----------------------------------------
# ライブラリの読み込み
#----------------------------------------
INCLUDE lib_ssh.sh

#----------------------------------------
# Main処理
#----------------------------------------

SSH_HOSTNAME=$2			# サーバホスト名
SSH_USERNAME=$3			# サーバユーザ名
SSH_LOGPASS=$4			# パスフレーズ
SSH_COMMAND=${@:5}		# リモートコマンド

SSH_LOGPASS=$(echo -n ${SSH_LOGPASS} | base64 -d)
if [ $? -ne 0 ]; then
	echo "パスワードのデコードに失敗しました。"${SCRIPT_NAME}"の処理を終了します。"
    exit ${FAIL_TO_DECODE_PASSWORD} 
fi

SSH_ACCESS "${SSH_HOSTNAME}" "${SSH_USERNAME}" "${SSH_LOGPASS}" "${SSH_COMMAND}"
exit $?