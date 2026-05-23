#!/usr/bin/env python3
"""
제약 조건별 실제 통과율 분석기
왜 고품질 조합이 0개인지 단계별 검증
"""

import random
import csv
from collections import Counter
import statistics

def get_frequent_numbers_all_time(filename='lotto_total.csv', top_n=25):
    """전체 회차에서 자주 나오는 번호들 추출"""
    try:
        frequent_nums = []
        with open(filename, encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # 헤더
            for row in reader:
                nums = row[3:9]  # 당첨번호 6개
                if all(n.isdigit() for n in nums):
                    frequent_nums.extend([int(n) for n in nums])
        
        counter = Counter(frequent_nums)
        return [num for num, count in counter.most_common(top_n)]
    except:
        return [34, 12, 13, 18, 27, 45, 33, 14, 40, 37, 7, 38]

def test_constraint_1_basic_structure(numbers):
    """1단계: 기본 구조 검증"""
    nums = sorted(numbers)
    
    # 1-1. 구간별 분배 체크
    ranges = [(1, 15), (16, 30), (31, 45)]
    for start, end in ranges:
        count = sum(1 for n in nums if start <= n <= end)
        if count < 1 or count > 3:
            return False, f"구간분배 실패: {start}-{end}구간에 {count}개"
    
    # 1-2. 홀짝 균형
    odds = sum(1 for n in nums if n % 2)
    if odds == 0 or odds == 6:
        return False, f"홀짝균형 실패: 홀수 {odds}개"
    
    # 1-3. 연속번호 제한
    consecutive = 1
    max_consecutive = 1
    for i in range(1, len(nums)):
        if nums[i] - nums[i-1] == 1:
            consecutive += 1
            max_consecutive = max(max_consecutive, consecutive)
        else:
            consecutive = 1
    if max_consecutive >= 4:
        return False, f"연속번호 실패: {max_consecutive}개 연속"
    
    # 1-4. 끝수 중복 제한
    last_digits = [n % 10 for n in nums]
    digit_counts = Counter(last_digits)
    if max(digit_counts.values()) >= 4:
        return False, f"끝수중복 실패: 최대 {max(digit_counts.values())}개 동일"
    
    return True, "1단계 통과"

def test_constraint_2_statistical(numbers):
    """2단계: 통계적 제약"""
    nums = sorted(numbers)
    
    # 2-1. 합계 범위
    total = sum(nums)
    if total < 145 or total > 165:
        return False, f"합계 실패: {total} (145~165 범위 벗어남)"
    
    # 2-2. 분산값 제한
    try:
        variance = statistics.variance(nums)
        if variance < 80 or variance > 250:
            return False, f"분산 실패: {variance:.1f} (80~250 범위 벗어남)"
    except:
        return False, "분산 계산 오류"
    
    # 2-3. 첫째자리 균형
    first_digits = [n // 10 for n in nums]
    first_digit_counts = Counter(first_digits)
    if max(first_digit_counts.values()) >= 3:
        return False, f"첫째자리 실패: 최대 {max(first_digit_counts.values())}개 집중"
    
    # 2-4. 끝수 특별제한
    ending_0_5 = sum(1 for n in nums if n % 10 in [0, 5])
    if ending_0_5 > 1:
        return False, f"0,5끝수 실패: {ending_0_5}개 (1개 이하)"
    
    return True, "2단계 통과"

def test_constraint_3_frequency(numbers):
    """3단계: 빈출번호 기반"""
    nums = sorted(numbers)
    
    # 3-1. 의무 포함
    frequent_top12 = get_frequent_numbers_all_time(top_n=12)
    frequent_count = sum(1 for n in nums if n in frequent_top12)
    if frequent_count < 2:
        return False, f"빈출번호 실패: {frequent_count}개 (최소 2개 필요)"
    
    # 3-2. 완전 배제
    all_frequent = get_frequent_numbers_all_time(top_n=45)
    low_frequent = all_frequent[-5:]
    low_frequent_count = sum(1 for n in nums if n in low_frequent)
    if low_frequent_count > 0:
        return False, f"저빈출번호 실패: {low_frequent_count}개 포함"
    
    return True, "3단계 통과"

def test_constraint_4_mathematical(numbers):
    """4단계: 수학적 패턴"""
    nums = sorted(numbers)
    
    # 4-1. 소수 제한
    primes_1_45 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
    prime_count = sum(1 for n in nums if n in primes_1_45)
    if prime_count < 1 or prime_count > 4:
        return False, f"소수 실패: {prime_count}개 (1~4개 범위)"
    
    # 4-2. 제곱수 제한
    squares = [1, 4, 9, 16, 25, 36]
    square_count = sum(1 for n in nums if n in squares)
    if square_count > 1:
        return False, f"제곱수 실패: {square_count}개 (1개 이하)"
    
    # 4-3. 5의 배수 제한
    multiples_of_5 = [5, 10, 15, 20, 25, 30, 35, 40, 45]
    multiple_5_count = sum(1 for n in nums if n in multiples_of_5)
    if multiple_5_count > 1:
        return False, f"5배수 실패: {multiple_5_count}개 (1개 이하)"
    
    # 4-4. 간격 패턴
    gaps = [nums[i+1] - nums[i] for i in range(5)]
    gap_counts = Counter(gaps)
    if max(gap_counts.values()) >= 2:
        return False, f"간격패턴 실패: 동일간격 {max(gap_counts.values())}회"
    
    return True, "4단계 통과"

def analyze_constraint_bottlenecks():
    """제약 조건별 병목 현상 분석"""
    print("=" * 70)
    print("🔍 제약 조건별 실제 통과율 분석")
    print("=" * 70)
    
    test_count = 10000
    stage_failures = {
        "1단계": 0, "2단계": 0, "3단계": 0, "4단계": 0, "전체통과": 0
    }
    
    failure_details = {}
    
    for i in range(test_count):
        # 랜덤 조합 생성
        nums = random.sample(range(1, 46), 6)
        
        # 1단계 테스트
        passed_1, msg_1 = test_constraint_1_basic_structure(nums)
        if not passed_1:
            stage_failures["1단계"] += 1
            failure_type = msg_1.split(":")[0]
            failure_details[failure_type] = failure_details.get(failure_type, 0) + 1
            continue
        
        # 2단계 테스트
        passed_2, msg_2 = test_constraint_2_statistical(nums)
        if not passed_2:
            stage_failures["2단계"] += 1
            failure_type = msg_2.split(":")[0]
            failure_details[failure_type] = failure_details.get(failure_type, 0) + 1
            continue
        
        # 3단계 테스트
        passed_3, msg_3 = test_constraint_3_frequency(nums)
        if not passed_3:
            stage_failures["3단계"] += 1
            failure_type = msg_3.split(":")[0]
            failure_details[failure_type] = failure_details.get(failure_type, 0) + 1
            continue
        
        # 4단계 테스트
        passed_4, msg_4 = test_constraint_4_mathematical(nums)
        if not passed_4:
            stage_failures["4단계"] += 1
            failure_type = msg_4.split(":")[0]
            failure_details[failure_type] = failure_details.get(failure_type, 0) + 1
            continue
        
        # 모든 단계 통과
        stage_failures["전체통과"] += 1
    
    # 결과 출력
    print(f"📊 테스트 조합 수: {test_count:,}개")
    print()
    
    for stage, failures in stage_failures.items():
        if stage == "전체통과":
            print(f"✅ {stage}: {failures}개 ({failures/test_count*100:.2f}%)")
        else:
            print(f"❌ {stage} 실패: {failures}개 ({failures/test_count*100:.2f}%)")
    
    print()
    print("🔍 주요 실패 원인 Top 10:")
    sorted_failures = sorted(failure_details.items(), key=lambda x: x[1], reverse=True)
    for i, (failure_type, count) in enumerate(sorted_failures[:10], 1):
        print(f"{i:2d}. {failure_type}: {count}회 ({count/test_count*100:.1f}%)")
    
    print("\n" + "=" * 70)
    
    # 병목 구간 확인
    if stage_failures["전체통과"] == 0:
        print("🚨 경고: 전체 통과 조합이 0개입니다!")
        print("   → 제약 조건이 너무 엄격하거나 상호 충돌하는 조건이 있을 수 있습니다.")
    elif stage_failures["전체통과"] < test_count * 0.001:  # 0.1% 미만
        print("⚠️  주의: 통과율이 매우 낮습니다!")
        print(f"   → 100,000번 시도 시 예상 통과: 약 {stage_failures['전체통과'] * 10}개")
    
    return stage_failures, failure_details

def analyze_specific_examples():
    """구체적인 실패 사례 분석"""
    print("\n" + "=" * 70)
    print("🎯 구체적인 실패 사례 분석")
    print("=" * 70)
    
    # 몇 가지 대표적인 조합들 테스트
    test_cases = [
        [1, 15, 16, 30, 31, 45],    # 구간별 균등 분배
        [3, 7, 12, 13, 34, 45],     # 빈출번호 위주
        [2, 8, 15, 23, 31, 42],     # 무작위
        [5, 10, 15, 20, 25, 30],    # 5의 배수들
        [1, 2, 3, 4, 5, 6],         # 연속번호
    ]
    
    case_names = ["구간균등", "빈출위주", "무작위", "5배수", "연속번호"]
    
    for i, (nums, name) in enumerate(zip(test_cases, case_names)):
        print(f"\n📋 사례 {i+1}: {name} - {nums}")
        
        passed_1, msg_1 = test_constraint_1_basic_structure(nums)
        print(f"   1단계: {'✅' if passed_1 else '❌'} {msg_1}")
        
        if passed_1:
            passed_2, msg_2 = test_constraint_2_statistical(nums)
            print(f"   2단계: {'✅' if passed_2 else '❌'} {msg_2}")
            
            if passed_2:
                passed_3, msg_3 = test_constraint_3_frequency(nums)
                print(f"   3단계: {'✅' if passed_3 else '❌'} {msg_3}")
                
                if passed_3:
                    passed_4, msg_4 = test_constraint_4_mathematical(nums)
                    print(f"   4단계: {'✅' if passed_4 else '❌'} {msg_4}")

if __name__ == "__main__":
    analyze_constraint_bottlenecks()
    analyze_specific_examples() 