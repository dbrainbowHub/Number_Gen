#!/usr/bin/env python3
"""
제약 조건들 간의 상호작용 분석
145~165 범위는 적절하지만 다른 제약과 결합 시 문제 발생
"""

import random
import csv
from collections import Counter
import statistics

def load_actual_winning_numbers():
    """실제 당첨번호들 로드"""
    winning_nums = []
    try:
        with open('lotto_total.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                try:
                    nums = [int(n) for n in row[3:9] if n.isdigit()]
                    if len(nums) == 6:
                        winning_nums.append(sorted(nums))
                except:
                    continue
    except:
        pass
    return winning_nums

def test_constraint_interactions():
    """제약 조건들 간의 상호작용 분석"""
    print("🎯 제약 조건 상호작용 분석")
    print("=" * 60)
    
    # 실제 당첨번호들 로드
    actual_wins = load_actual_winning_numbers()
    print(f"📊 실제 당첨번호 {len(actual_wins)}개로 분석")
    
    # 각 제약 조건별로 실제 당첨번호들이 통과하는지 확인
    constraints_results = {
        "합계_145-165": 0,
        "구간분배_1-3개": 0,
        "빈출번호_최소2개": 0,
        "저빈출_완전배제": 0,
        "첫째자리_최대2개": 0,
        "홀짝균형": 0,
        "연속번호_3개이하": 0,
        "전체통과": 0
    }
    
    # 빈출번호 데이터 (근사)
    frequent_top12 = [34, 12, 13, 18, 27, 45, 33, 14, 40, 37, 7, 38]
    low_frequent = [41, 42, 44, 26, 36]
    
    for nums in actual_wins:
        # 1. 합계 범위
        total = sum(nums)
        if 145 <= total <= 165:
            constraints_results["합계_145-165"] += 1
        
        # 2. 구간 분배
        ranges = [(1, 15), (16, 30), (31, 45)]
        valid_ranges = True
        for start, end in ranges:
            count = sum(1 for n in nums if start <= n <= end)
            if count < 1 or count > 3:
                valid_ranges = False
                break
        if valid_ranges:
            constraints_results["구간분배_1-3개"] += 1
        
        # 3. 빈출번호
        frequent_count = sum(1 for n in nums if n in frequent_top12)
        if frequent_count >= 2:
            constraints_results["빈출번호_최소2개"] += 1
        
        # 4. 저빈출 배제
        low_count = sum(1 for n in nums if n in low_frequent)
        if low_count == 0:
            constraints_results["저빈출_완전배제"] += 1
        
        # 5. 첫째자리
        first_digits = [n // 10 for n in nums]
        if max(Counter(first_digits).values()) <= 2:
            constraints_results["첫째자리_최대2개"] += 1
        
        # 6. 홀짝균형
        odds = sum(1 for n in nums if n % 2)
        if 1 <= odds <= 5:  # 0, 6 제외
            constraints_results["홀짝균형"] += 1
        
        # 7. 연속번호
        consecutive = 1
        max_consecutive = 1
        for i in range(1, len(nums)):
            if nums[i] - nums[i-1] == 1:
                consecutive += 1
                max_consecutive = max(max_consecutive, consecutive)
            else:
                consecutive = 1
        if max_consecutive <= 3:
            constraints_results["연속번호_3개이하"] += 1
        
        # 전체 통과 (핵심 제약들만)
        if (145 <= total <= 165 and valid_ranges and frequent_count >= 2 and 
            low_count == 0 and max(Counter(first_digits).values()) <= 2):
            constraints_results["전체통과"] += 1
    
    print("\n📊 실제 당첨번호들의 제약 조건 통과율:")
    total_wins = len(actual_wins)
    
    for constraint, count in constraints_results.items():
        rate = count / total_wins * 100
        if constraint == "전체통과":
            print(f"✅ {constraint}: {count}개 ({rate:.1f}%)")
        else:
            print(f"   {constraint}: {count}개 ({rate:.1f}%)")
    
    return constraints_results

def analyze_constraint_conflicts():
    """제약 조건들 간의 충돌 분석"""
    print(f"\n" + "=" * 60)
    print("🔍 제약 조건 충돌 분석")
    print("=" * 60)
    
    # 실제 당첨번호들로 분석
    actual_wins = load_actual_winning_numbers()
    
    # 각 조합별로 어떤 제약에서 실패하는지 분석
    failure_patterns = {}
    
    frequent_top12 = [34, 12, 13, 18, 27, 45, 33, 14, 40, 37, 7, 38]
    low_frequent = [41, 42, 44, 26, 36]
    
    for nums in actual_wins:
        failures = []
        
        # 각 제약 조건 체크
        total = sum(nums)
        if not (145 <= total <= 165):
            failures.append("합계범위")
        
        # 구간분배
        ranges = [(1, 15), (16, 30), (31, 45)]
        for start, end in ranges:
            count = sum(1 for n in nums if start <= n <= end)
            if count < 1 or count > 3:
                failures.append("구간분배")
                break
        
        # 빈출번호
        frequent_count = sum(1 for n in nums if n in frequent_top12)
        if frequent_count < 2:
            failures.append("빈출번호")
        
        # 저빈출
        low_count = sum(1 for n in nums if n in low_frequent)
        if low_count > 0:
            failures.append("저빈출")
        
        # 첫째자리
        first_digits = [n // 10 for n in nums]
        if max(Counter(first_digits).values()) > 2:
            failures.append("첫째자리")
        
        # 실패 패턴 기록
        if failures:
            pattern = "+".join(sorted(failures))
            failure_patterns[pattern] = failure_patterns.get(pattern, 0) + 1
    
    print("주요 실패 패턴 (실제 당첨번호 기준):")
    sorted_patterns = sorted(failure_patterns.items(), key=lambda x: x[1], reverse=True)
    
    for pattern, count in sorted_patterns[:10]:
        rate = count / len(actual_wins) * 100
        print(f"   {pattern}: {count}회 ({rate:.1f}%)")
    
    # 가장 문제가 되는 제약 조합 찾기
    print(f"\n💡 결론:")
    if "합계범위" in sorted_patterns[0][0]:
        print("   🎯 합계범위(145~165)는 적절하지만 다른 제약과 결합 시 과도함")
    else:
        print("   ✅ 합계범위(145~165)는 단독으로는 적절함")

if __name__ == "__main__":
    results = test_constraint_interactions()
    analyze_constraint_conflicts() 