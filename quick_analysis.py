#!/usr/bin/env python3
"""
빠른 제약 조건 분석 - 왜 0개인지 핵심 원인만 파악
"""

import random
from collections import Counter
import statistics

def quick_stage_analysis():
    """핵심 제약 조건들만 빠르게 분석"""
    print("🎯 핵심 제약 조건 분석 (10,000개 샘플)")
    print("=" * 60)
    
    test_count = 10000
    results = {
        "합계범위_145-165": 0,
        "구간분배_1-3개": 0, 
        "빈출번호_최소2개": 0,
        "저빈출_완전배제": 0,
        "분산_80-250": 0,
        "첫째자리_최대2개": 0,
        "연속번호_3개이하": 0,
        "전체통과": 0
    }
    
    # 빈출번호 (실제 데이터 근사)
    frequent_top12 = [34, 12, 13, 18, 27, 45, 33, 14, 40, 37, 7, 38]
    low_frequent = [41, 42, 44, 26, 36]  # 하위 5개
    
    for i in range(test_count):
        nums = sorted(random.sample(range(1, 46), 6))
        
        # 1. 합계 범위
        total = sum(nums)
        if 145 <= total <= 165:
            results["합계범위_145-165"] += 1
        
        # 2. 구간 분배
        ranges = [(1, 15), (16, 30), (31, 45)]
        valid_ranges = True
        for start, end in ranges:
            count = sum(1 for n in nums if start <= n <= end)
            if count < 1 or count > 3:
                valid_ranges = False
                break
        if valid_ranges:
            results["구간분배_1-3개"] += 1
        
        # 3. 빈출번호
        frequent_count = sum(1 for n in nums if n in frequent_top12)
        if frequent_count >= 2:
            results["빈출번호_최소2개"] += 1
        
        # 4. 저빈출 배제
        low_count = sum(1 for n in nums if n in low_frequent)
        if low_count == 0:
            results["저빈출_완전배제"] += 1
        
        # 5. 분산
        try:
            var = statistics.variance(nums)
            if 80 <= var <= 250:
                results["분산_80-250"] += 1
        except:
            pass
        
        # 6. 첫째자리
        first_digits = [n // 10 for n in nums]
        if max(Counter(first_digits).values()) <= 2:
            results["첫째자리_최대2개"] += 1
        
        # 7. 연속번호
        consecutive = 1
        max_consecutive = 1
        for j in range(1, len(nums)):
            if nums[j] - nums[j-1] == 1:
                consecutive += 1
                max_consecutive = max(max_consecutive, consecutive)
            else:
                consecutive = 1
        if max_consecutive <= 3:
            results["연속번호_3개이하"] += 1
        
        # 전체 통과 (핵심 조건들만)
        if (145 <= total <= 165 and valid_ranges and frequent_count >= 2 and 
            low_count == 0 and 80 <= statistics.variance(nums) <= 250):
            results["전체통과"] += 1
    
    print("📊 각 제약 조건별 통과율:")
    for condition, count in results.items():
        rate = count / test_count * 100
        if condition == "전체통과":
            print(f"✅ {condition}: {count}개 ({rate:.2f}%)")
        else:
            print(f"   {condition}: {count}개 ({rate:.1f}%)")
    
    print(f"\n🎯 100,000번 시도 시 예상 통과: {results['전체통과'] * 10}개")
    
    # 병목 구간 확인
    bottlenecks = []
    for condition, count in results.items():
        if condition != "전체통과":
            rate = count / test_count * 100
            if rate < 50:  # 50% 미만 통과율
                bottlenecks.append((condition, rate))
    
    bottlenecks.sort(key=lambda x: x[1])
    
    print(f"\n🚨 주요 병목 구간 (통과율 낮은 순):")
    for i, (condition, rate) in enumerate(bottlenecks[:5], 1):
        print(f"{i}. {condition}: {rate:.1f}% 통과")

def multiplication_effect():
    """제약 조건들의 곱셈 효과 분석"""
    print(f"\n" + "=" * 60)
    print("🔢 제약 조건 곱셈 효과 분석")
    print("=" * 60)
    
    # 각 제약 조건의 대략적인 통과율 (위 분석 기반 추정)
    constraints = {
        "합계범위": 0.20,      # 20%
        "구간분배": 0.65,      # 65%  
        "빈출번호": 0.75,      # 75%
        "저빈출배제": 0.80,    # 80%
        "분산범위": 0.65,      # 65%
        "첫째자리": 0.55,      # 55%
        "연속번호": 0.85,      # 85%
        "소수제약": 0.70,      # 70% (추정)
        "중복방지": 0.80,      # 80% (추정)
    }
    
    cumulative = 1.0
    print("단계별 누적 통과율:")
    
    for i, (name, rate) in enumerate(constraints.items(), 1):
        cumulative *= rate
        percentage = cumulative * 100
        print(f"{i}단계 {name}: {rate*100:.0f}% → 누적 {percentage:.4f}%")
    
    final_expected = int(cumulative * 100000)
    print(f"\n🎯 최종 예상 통과: {final_expected}개 (100,000번 시도 기준)")
    
    if final_expected < 10:
        print("🚨 결론: 제약 조건들의 곱셈 효과로 실제 통과가 거의 불가능!")
        print("   → 각각은 합리적이지만 모두 합쳐지면 너무 엄격함")

if __name__ == "__main__":
    quick_stage_analysis()
    multiplication_effect() 