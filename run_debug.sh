#!/bin/bash

echo "🔍 로또 생성기 디버깅 시작..."
echo "현재 시간: $(date)"
echo "현재 디렉토리: $(pwd)"
echo "현재 사용자: $(whoami)"

# 파일 권한 설정
chmod +x debug_lotto.py

# Python 실행
echo "Python3으로 디버깅 스크립트 실행..."
python3 debug_lotto.py

# 결과 확인
if [ -f "debug_output.log" ]; then
    echo "✅ 디버깅 로그 생성됨"
    echo "마지막 10줄:"
    tail -10 debug_output.log
else
    echo "❌ 디버깅 로그 생성 실패"
fi

echo "🔍 디버깅 완료!" 