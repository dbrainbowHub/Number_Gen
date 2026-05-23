#!/usr/bin/env python3
"""
수정된 lotto_generator.py 테스트 스크립트
"""

import subprocess
import sys
import datetime

def test_lotto_generator():
    print("=" * 50)
    print("🎲 수정된 lotto_generator.py 테스트")
    print("=" * 50)
    print(f"테스트 시작: {datetime.datetime.now()}")
    
    try:
        # lotto_generator.py 실행
        result = subprocess.run([sys.executable, 'lotto_generator.py'], 
                               capture_output=True, text=True, timeout=120)
        
        print(f"Return code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ 실행 성공!")
            if result.stdout:
                print(f"출력 내용:\n{result.stdout}")
        else:
            print("❌ 실행 실패!")
            if result.stderr:
                print(f"오류 내용:\n{result.stderr}")
                
        # lotto_result.txt 파일 확인
        try:
            with open('lotto_result.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"\n📄 lotto_result.txt 마지막 10줄:")
                for line in lines[-10:]:
                    print(f"  {line.strip()}")
        except Exception as e:
            print(f"❌ lotto_result.txt 읽기 실패: {e}")
            
    except subprocess.TimeoutExpired:
        print("❌ 실행 시간 초과 (2분)")
    except Exception as e:
        print(f"❌ 테스트 중 오류: {e}")
    
    print("\n🔍 테스트 완료!")

if __name__ == "__main__":
    test_lotto_generator() 