#!/usr/bin/env python3
"""
lotto_generator.py 실행 오류 디버깅 스크립트
"""

import sys
import traceback
import os
import subprocess
import datetime

def debug_environment():
    """실행 환경 확인"""
    print("=" * 50)
    print("🔍 실행 환경 디버깅")
    print("=" * 50)
    
    print(f"현재 시간: {datetime.datetime.now()}")
    print(f"Python 버전: {sys.version}")
    print(f"현재 작업 디렉토리: {os.getcwd()}")
    print(f"Python 경로: {sys.executable}")
    
    # 필요한 모듈 확인
    modules = ['pandas', 'csv', 'random', 'collections', 'os', 're', 'datetime']
    print("\n📦 모듈 확인:")
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}: OK")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
    
    # 파일 존재 확인
    print("\n📁 파일 확인:")
    files = ['lotto_total.csv', 'lotto_generator.py', 'lotto_result.txt']
    for file in files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"  ✅ {file}: {size} bytes")
        else:
            print(f"  ❌ {file}: 파일 없음")

def debug_lotto_generator():
    """lotto_generator.py 실행 디버깅"""
    print("\n" + "=" * 50)
    print("🎲 lotto_generator.py 실행 테스트")
    print("=" * 50)
    
    try:
        # 먼저 모듈 import 테스트
        print("1️⃣ 모듈 import 테스트...")
        import csv
        import random
        from collections import Counter
        import os
        import re
        import datetime
        print("  ✅ 기본 모듈 import 성공")
        
        # CSV 파일 읽기 테스트
        print("\n2️⃣ CSV 파일 읽기 테스트...")
        if os.path.exists('lotto_total.csv'):
            with open('lotto_total.csv', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
                first_row = next(reader)
                print(f"  ✅ CSV 파일 읽기 성공: {len(header)}개 컬럼")
                print(f"  첫 번째 행: {first_row}")
        else:
            print("  ❌ lotto_total.csv 파일이 없습니다")
            
        # lotto_generator.py 직접 실행
        print("\n3️⃣ lotto_generator.py 직접 실행...")
        result = subprocess.run([sys.executable, 'lotto_generator.py'], 
                               capture_output=True, text=True, timeout=60)
        
        print(f"  Return code: {result.returncode}")
        if result.stdout:
            print(f"  STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"  STDERR:\n{result.stderr}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print(f"오류 타입: {type(e).__name__}")
        print("상세 트레이스백:")
        traceback.print_exc()

def main():
    """메인 디버깅 함수"""
    try:
        # 로그 파일 생성
        with open('debug_output.log', 'w', encoding='utf-8') as f:
            # 표준 출력을 파일로도 저장
            class Tee:
                def __init__(self, *files):
                    self.files = files
                def write(self, obj):
                    for f in self.files:
                        f.write(obj)
                        f.flush()
                def flush(self):
                    for f in self.files:
                        f.flush()
            
            original_stdout = sys.stdout
            sys.stdout = Tee(sys.stdout, f)
            
            debug_environment()
            debug_lotto_generator()
            
            sys.stdout = original_stdout
            
        print("\n✅ 디버깅 완료! debug_output.log 파일을 확인하세요.")
        
    except Exception as e:
        print(f"❌ 디버깅 중 오류: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 