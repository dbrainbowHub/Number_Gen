#!/usr/bin/env python3
"""
로또 생성기 8단계 제약 조건 실제 통과율 계산기
왜 고품질 조합이 0개인지 정확한 원인 분석
"""

import random
import csv
from collections import Counter
import statistics
import math

def load_past_results():
    """과거 당첨번호 + 과거 추천번호 로드"""
    all_combos = set()
    
    # 과거 당첨번호
    try:
        with open('lotto_total.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                nums = tuple(sorted([int(n) for n in row[3:9] if n.isdigit()]))
                if len(nums) == 6:
                    all_combos.add(nums)
    except:
        pass
    
    # 과거 추천번호
    try:
        with open('lotto_result.txt', encoding='utf-8') as f:
            for line in f:
                if '추천번호' in line and '[' in line:
                    start = line.find('[')
                    end = line.find(']')
                    if start != -1 and end != -1:
                        nums_str = line[start+1:end]
                        nums = tuple(sorted([int(n.strip()) for n in nums_str.split(',')]))
                        if len(nums) == 6:
                            all_combos.add(nums)
    except:
        pass
    
    return all_combos

def get_frequent_numbers_all_time():
    """빈출번호 데이터 로드"""
    try:
        frequent_nums = []
        with open('lotto_total.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                nums = [int(n) for n in row[3:9] if n.isdigit()]
                frequent_nums.extend(nums)
        
        counter = Counter(frequent_nums)
        all_nums_by_freq = [num for num, count in counter.most_common()]
        return all_nums_by_freq
    except:
        return list(range(1, 46))

def check_all_8_stages(numbers):
    """8단계 제약 조건 전체 검사"""
    nums = sorted(numbers)
    past_combos = load_past_results()
    frequent_nums = get_frequent_numbers_all_time()
    
    # 1단계: 기본 구조
    if not check_stage_1_basic(nums):
        return False, "1단계 실패"
    
    # 2단계: 통계적 제약
    if not check_stage_2_statistical(nums):
        return False, "2단계 실패"
    
    # 3단계: 빈출번호 기반
    if not check_stage_3_frequency(nums, frequent_nums):
        return False, "3단계 실패"
    
    # 4단계: 수학적 패턴
    if not check_stage_4_mathematical(nums):
        return False, "4단계 실패"
    
    # 5단계: 고급 수학적 제약
    if not check_stage_5_advanced_math(nums):
        return False, "5단계 실패"
    
    # 6단계: 패턴 유사성
    if not check_stage_6_pattern_similarity(nums):
        return False, "6단계 실패"
    
    # 7단계: 중복 방지
    if tuple(nums) in past_combos:
        return False, "7단계 실패"
    
    # 8단계: Top5 특별규칙
    if not check_stage_8_top5_rules(nums, frequent_nums):
        return False, "8단계 실패"
    
    return True, "전체 통과"

def check_stage_1_basic(nums):
    """1단계: 기본 구조"""
    # 구간별 분배
    ranges = [(1, 15), (16, 30), (31, 45)]
    for start, end in ranges:
        count = sum(1 for n in nums if start <= n <= end)
        if count < 1 or count > 3:
            return False
    
    # 홀짝 균형
    odds = sum(1 for n in nums if n % 2)
    if odds == 0 or odds == 6:
        return False
    
    # 연속번호 제한
    consecutive = 1
    max_consecutive = 1
    for i in range(1, len(nums)):
        if nums[i] - nums[i-1] == 1:
            consecutive += 1
            max_consecutive = max(max_consecutive, consecutive)
        else:
            consecutive = 1
    if max_consecutive >= 4:
        return False
    
    # 끝수 중복
    last_digits = [n % 10 for n in nums]
    if max(Counter(last_digits).values()) >= 4:
        return False
    
    return True

def check_stage_2_statistical(nums):
    """2단계: 통계적 제약"""
    # 합계 범위
    if sum(nums) < 145 or sum(nums) > 165:
        return False
    
    # 분산값
    try:
        if statistics.variance(nums) < 80 or statistics.variance(nums) > 250:
            return False
    except:
        return False
    
    # 첫째자리 균형
    first_digits = [n // 10 for n in nums]
    if max(Counter(first_digits).values()) >= 3:
        return False
    
    # 0,5 끝수 제한
    ending_0_5 = sum(1 for n in nums if n % 10 in [0, 5])
    if ending_0_5 > 1:
        return False
    
    return True

def check_stage_3_frequency(nums, frequent_nums):
    """3단계: 빈출번호 기반"""
    top_12 = frequent_nums[:12]
    bottom_5 = frequent_nums[-5:]
    
    # 상위 12개 중 최소 2개
    if sum(1 for n in nums if n in top_12) < 2:
        return False
    
    # 하위 5개 완전 배제
    if any(n in bottom_5 for n in nums):
        return False
    
    return True

def check_stage_4_mathematical(nums):
    """4단계: 수학적 패턴"""
    # 소수 제한
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
    prime_count = sum(1 for n in nums if n in primes)
    if prime_count < 1 or prime_count > 4:
        return False
    
    # 제곱수 제한
    squares = [1, 4, 9, 16, 25, 36]
    if sum(1 for n in nums if n in squares) > 1:
        return False
    
    # 5의 배수 제한
    multiples_5 = [5, 10, 15, 20, 25, 30, 35, 40, 45]
    if sum(1 for n in nums if n in multiples_5) > 1:
        return False
    
    # 간격 패턴
    gaps = [nums[i+1] - nums[i] for i in range(5)]
    if max(Counter(gaps).values()) >= 2:
        return False
    
    return True

def check_stage_5_advanced_math(nums):
    """5단계: 고급 수학적 제약"""
    # 피보나치수
    fibonacci = [1, 2, 3, 5, 8, 13, 21, 34]
    if sum(1 for n in nums if n in fibonacci) > 2:
        return False
    
    # 삼각수
    triangular = [1, 3, 6, 10, 15, 21, 28, 36, 45]
    if sum(1 for n in nums if n in triangular) > 2:
        return False
    
    # 등차수열 체크
    gaps = [nums[i+1] - nums[i] for i in range(5)]
    if len(set(gaps)) <= 2:  # 너무 규칙적
        return False
    
    # 자릿수 합
    digit_sums = [sum(int(d) for d in str(n)) for n in nums]
    if max(Counter(digit_sums).values()) >= 3:
        return False
    
    # 대칭성 체크
    if nums[0] + nums[5] == nums[1] + nums[4] == nums[2] + nums[3]:
        return False
    
    return True

def check_stage_6_pattern_similarity(nums):
    """6단계: 패턴 유사성 배제"""
    # 산술/기하급수 패턴
    gaps = [nums[i+1] - nums[i] for i in range(5)]
    
    # 등차수열
    if len(set(gaps)) == 1:
        return False
    
    # 기하급수적 증가
    ratios = []
    for i in range(1, len(gaps)):
        if gaps[i-1] != 0:
            ratios.append(gaps[i] / gaps[i-1])
    if len(set([round(r, 1) for r in ratios])) <= 1 and len(ratios) > 2:
        return False
    
    return True

def check_stage_8_top5_rules(nums, frequent_nums):
    """8단계: Top5 특별규칙"""
    top_5 = frequent_nums[:5]
    
    # Top5에서 3개 이상 선택 시 특별규칙
    top5_count = sum(1 for n in nums if n in top_5)
    if top5_count >= 3:
        # 특별 제약들 (예시)
        if sum(nums) < 150:  # 더 높은 합계 요구
            return False
        if max(nums) - min(nums) < 25:  # 더 넓은 분포 요구
            return False
        
    return True

def analyze_8_stage_bottlenecks():
    """8단계 제약 조건 병목 분석"""
    print("=" * 80)
    print("🎯 로또 생성기 8단계 제약 조건 실제 통과율 분석")
    print("=" * 80)
    
    test_count = 50000  # 더 많은 테스트
    stage_results = {
        "1단계": 0, "2단계": 0, "3단계": 0, "4단계": 0,
        "5단계": 0, "6단계": 0, "7단계": 0, "8단계": 0,
        "전체통과": 0
    }
    
    for i in range(test_count):
        if (i + 1) % 10000 == 0:
            print(f"진행률: {i+1:,}/{test_count:,} ({(i+1)/test_count*100:.1f}%)")
        
        nums = sorted(random.sample(range(1, 46), 6))
        passed, stage = check_all_8_stages(nums)
        
        if passed:
            stage_results["전체통과"] += 1
        else:
            # "1단계 실패" -> "1단계"
            stage_name = stage.replace(" 실패", "")
            if stage_name in stage_results:
                stage_results[stage_name] += 1
    
    print("\n" + "=" * 80)
    print("📊 8단계 제약 조건별 실패율")
    print("=" * 80)
    
    total_tests = test_count
    cumulative_pass = test_count
    
    for stage in ["1단계", "2단계", "3단계", "4단계", "5단계", "6단계", "7단계", "8단계"]:
        failures = stage_results[stage]
        fail_rate = failures / total_tests * 100
        cumulative_pass -= failures
        cumulative_rate = cumulative_pass / total_tests * 100
        
        print(f"{stage}: {failures:,}개 실패 ({fail_rate:.2f}%) | 누적통과: {cumulative_pass:,}개 ({cumulative_rate:.4f}%)")
    
    final_pass = stage_results["전체통과"]
    final_rate = final_pass / total_tests * 100
    
    print(f"\n✅ 최종 전체 통과: {final_pass}개 ({final_rate:.6f}%)")
    print(f"🎯 100,000번 시도 시 예상 통과: {int(final_rate * 1000)}개")
    
    if final_pass == 0:
        print("\n🚨 결론: 제약 조건이 너무 엄격하여 실제로는 통과 불가능!")
        print("   → 이론적으로는 가능하지만 확률이 극도로 낮음")
    
    return stage_results

if __name__ == "__main__":
    analyze_8_stage_bottlenecks() 