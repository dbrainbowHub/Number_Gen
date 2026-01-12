#!/bin/bash

# 기존 봇 프로세스 종료
echo "기존 봇 프로세스를 종료합니다..."
pkill -f discord_lotto_bot.py

# 잠시 대기
sleep 2

# 새로운 봇 실행
echo "새로운 봇을 백그라운드로 시작합니다..."
nohup python3 discord_lotto_bot.py > bot_output.log 2>&1 &

# 프로세스 ID 저장
echo $! > bot_pid.txt

echo "봇이 백그라운드로 시작되었습니다. PID: $(cat bot_pid.txt)"
echo "로그를 확인하려면: tail -f bot_output.log"
echo "봇을 종료하려면: ./stop_bot.sh" 