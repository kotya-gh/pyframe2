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
# [lib_ssh]パスワード引き渡し(ssh接続)
# 
# ssh接続時のパスワードを環境変数に設定し，sshへ引き渡す。次の形式で使用する。
# echo password | /usr/tools/bin/ssh_pass.sh ssh shelladmin@192.168.0.100
# 
# @access public
# @param なし
# @return なし
# @see なし
# @throws なし
#
if [ -n "$PASSWORD" ]; then
    cat <<< "$PASSWORD"
    exit 0
fi
read PASSWORD
export SSH_ASKPASS=$0
export PASSWORD
export DISPLAY=dummy:0
exec setsid "$@"