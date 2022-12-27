#!/bin/bash
##
# [procnum]プロセス数出力処理
# 
# $2で指定したプロセスの稼働数を標準出力する。
# プロセス数取得成功時は終了コード0で終了する。
# 
# @access public
# @param string $1 ROOTパス
# @param string $2 検索プロセス名
# @return psコマンド終了コード
# @see ps aux
# @throws なし
#
#----------------------------------------
# 初期設定
#----------------------------------------
if [ $# -le 1 ]; then
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

#----------------------------------------
# Main処理
#----------------------------------------

# プロセス名
PROCNAME=${@:2}
# 本スクリプトのフルパス
SCRIPT_PATH=${BIN_PATH}${SCRIPT_NAME}
#ps aux | grep "${PROCNAME}" | grep -v "\(${SCRIPT_PATH}\|grep\)" | wc -l
pgrep -x "${PROCNAME}" -f -c
exit $?