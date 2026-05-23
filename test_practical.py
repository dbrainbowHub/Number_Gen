#!/usr/bin/env python3
"""
실용적 lotto_generator_relaxed.py 테스트 스크립트
"""

import subprocess
import sys
import datetime

def test_practical_generator():
    print("=" * 60)
    print("🎯 실용적 로또 생성기 테스트 (완화된 제약조건)")
    print("=" * 60)
    print(f"테스트 시작: {datetime.datetime.now()}")
    
    try:
        # 실용적 버전 실행
        result = subprocess.run([sys.executable, 'lotto_generator_relaxed.py'], 
                               capture_output=True, text=True, timeout=60)
        
        print(f"Return code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ 실행 성공!")
            if result.stdout:
                print(f"출력 내용:\n{result.stdout}")
        else:
            print("❌ 실행 실패!")
            if result.stderr:
                print(f"오류 내용:\n{result.stderr}")
                
    except subprocess.TimeoutExpired:
        print("❌ 실행 시간 초과 (1분)")
    except Exception as e:
        print(f"❌ 테스트 중 오류: {e}")
    
    print("\n" + "=" * 60)
    print("🔍 실용적 버전 테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    test_practical_generator() 