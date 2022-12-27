#!/bin/bash
##
# [lib_ssh]ssh用ライブラリ
#
# SSHでリモートアクセスするためのライブラリです。
#
# @access public
# @author - <-@->
# @copyright MIT
# @category ユーザスクリプト実行処理
# @package なし
#

##
# [lib_ssh]リモートコマンドの実行
# 
# SSH経由でコマンドを発行し、結果を取得する。
# 接続失敗時、コード「SRV_CONNECT_ERR」を返す。
# 
# @access public
# @param string SSH_HOSTNAME 接続先ホスト名（IPアドレス）
# @param string SSH_USERNAME ユーザ名
# @param string SSH_LOGPASS ログインパスワード
# @param string SSH_COMMAND 実行コマンド
# @return string STATUS_OUT コマンド実行結果
# @see SSH_PASS
# @throws なし
#
SSH_MSG002001='リモートコマンド実行に失敗しました。処理を終了します。'

SSH_ACCESS ()
{
	# ローカル変数宣言
	STATUS_OUT=""			# コマンド実行結果
	SSH_HOSTNAME=$1			# サーバホスト名
	SSH_USERNAME=$2			# サーバユーザ名
	SSH_LOGPASS=$3			# パスフレーズ
	SSH_COMMAND=${@:4}		# リモートコマンド

	#---------------------------------------------------------------------------
	# リモートコマンド発行・格納処理
	#---------------------------------------------------------------------------
	# SSH接続後、リモートコマンドを発行し、変数へ実行結果を格納する

	STATUS_OUT=$( echo ${SSH_LOGPASS} | ${SSH_PASS} \
			${SSH} -tt -o "StrictHostKeyChecking=no" ${SSH_USERNAME}@${SSH_HOSTNAME} \
			"${SSH_COMMAND}" )
	RC=$?

	if [ 0 -eq "${RC}" ]
	then
		# コマンド実行結果を出力する
		echo "${STATUS_OUT}"
		return ${NORMAL_END}
	else
		# コマンド実行異常メッセージ出力
		# OUTPUT_LOCAL_LOG ${SSH_MSG002001}
		echo "${SSH_MSG002001}"
		return ${SRV_CONNECT_ERR}
	fi
}