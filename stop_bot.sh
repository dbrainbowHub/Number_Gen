#!/bin/bash


# PID 파일이 있는지 확인
if [ -f bot_pid.txt ]; then
    PID=$(cat bot_pid.txt)
    echo "봇 프로세스를 종료합니다... (PID: $PID)"
    kill $PID
    rm bot_pid.txt
    echo "봇이 종료되었습니다."
else
    echo "실행 중인 봇을 찾을 수 없습니다. 강제로 종료를 시도합니다..."
    pkill -f discord_lotto_bot.py
    echo "완료!"
fi 