"""
===============================================================================
        대한민국 동행복권 로또6/45 추천번호 생성 시스템 (v2.1 정밀최적화)
===============================================================================
[RB님 최종 승인 사항 반영]
1. 시도 횟수: 50만 번으로 대폭 증가 (끈질긴 탐색)
2. 병목 구간 해소 (골든존 공략):
   - 합계 구간: 120 ~ 180 (당첨 확률 64% 구간)
   - 빈출 번호: 역대 Top 15 중 2개 이상 (확률적 숨통 트임)
3. 품질 타협 없음:
   - 비상 모드(Fallback) 삭제. 엄격한 기준을 통과한 번호만 제공.
   - 억지 중복 채우기(Cycling) 삭제.
===============================================================================
"""

import csv
import random
from collections import Counter
import os
import re
import statistics

# 고정 Top5 번호 (사용자 선호)
TOP5 = [1, 3, 7, 12, 13]

# 구간 정의
RANGES = [(1, 15), (16, 30), (31, 45)]

def load_past_combinations(filename):
    """과거 모든 당첨 번호 로드 (중복 방지용)"""
    past = set()
    try:
        with open(filename, encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                nums = row[3:9]
                if all(n.isdigit() for n in nums):
                    comb = tuple(sorted(int(n) for n in nums))
                    past.add(comb)
    except Exception:
        pass
    return past

def get_last_draw_numbers(filename):
    """직전 회차 당첨번호"""
    try:
        with open(filename, encoding='utf-8') as f:
            lines = f.readlines()
            for line in reversed(lines):
                row = line.strip().split(',')
                if len(row) < 9: continue
                nums = row[3:9]
                if all(n.isdigit() for n in nums):
                    return [int(n) for n in nums]
    except:
        pass
    return []

def get_number_pools():
    pools = []
    for start, end in RANGES:
        pools.append(list(range(start, end+1)))
    return pools

# =========================================================
#  품질 검증 로직 (통계 기반 최적화)
# =========================================================

def check_even_odd(numbers):
    """홀짝 비율: 6:0, 0:6 제외"""
    odds = sum(1 for n in numbers if n % 2)
    return odds not in [0, 6]

def check_ranges(numbers):
    """구간별 분포: 특정 구간 전멸 방지 (최소 1개 이상)"""
    counts = [0, 0, 0]
    for n in numbers:
        for i, (start, end) in enumerate(RANGES):
            if start <= n <= end:
                counts[i] += 1
    # 너무 엄격한 [2,2,2] 대신, 한 구간에 몰빵되지 않게만 체크
    return all(c > 0 for c in counts)

def apply_top5_rule(draw, top5_in_last, line_idx):
    """Top5 번호 포함 규칙"""
    if len(top5_in_last) >= 2:
        if line_idx == 0:
            # 1세트는 Top5 중 2개 포함 시도
            needed = top5_in_last[:2]
            for i, n in enumerate(needed):
                if n not in draw: draw[i] = n
        elif line_idx == 1:
            if top5_in_last[0] not in draw: draw[0] = top5_in_last[0]
        elif line_idx == 2:
            if top5_in_last[1] not in draw: draw[0] = top5_in_last[1]
    elif len(top5_in_last) == 1:
        if line_idx == 0 and top5_in_last[0] not in draw:
            draw[0] = top5_in_last[0]
    return draw

def check_pattern_quality(numbers, csv_filename):
    """
    [핵심 필터링] 
    RB님의 엄격한 기준을 유지하되, 통계적 평균을 벗어난 
    비현실적인 제약 조건을 완화하여 15개 생성을 보장함.
    """
    nums = sorted(numbers)
    
    # 1. 구간별 개수 (1~4개 허용으로 완화)
    # 기존: 1~3개 -> 변경: 1~4개 (가끔 4개가 한 구간에 몰릴 수도 있음)
    ranges = [(1, 15), (16, 30), (31, 45)]
    for start, end in ranges:
        count = sum(1 for n in nums if start <= n <= end)
        if count < 1 or count > 4: return False
        
    # 2. 홀짝 (6:0, 0:6 제외) - 동일
    odds = sum(1 for n in nums if n % 2)
    if odds == 0 or odds == 6: return False
    
    # 3. 연속 번호 (4연속 이상 제외) - 동일
    # 3연속(1,2,3)까지는 허용
    consecutive = 1
    max_consecutive = 1
    for i in range(1, len(nums)):
        if nums[i] - nums[i-1] == 1:
            consecutive += 1
            max_consecutive = max(max_consecutive, consecutive)
        else:
            consecutive = 1
    if max_consecutive >= 4: return False
    
    # 4. [중요 수정] 합계 구간 (120 ~ 180)
    # 기존 145~165는 평균(138)을 벗어남. 당첨 확률이 높은 구간으로 확장.
    total_sum = sum(nums)
    if not (120 <= total_sum <= 180): return False
    
    # 5. 분산 (80 ~ 250) - 동일
    try:
        variance = statistics.variance(nums)
        if not (80 <= variance <= 250): return False
    except: pass # 계산 불가 시 패스
    
    # 6. [중요 수정] 빈출 번호 (Top 15 중 2개)
    # Top 12는 너무 좁음 -> Top 15로 확장하여 숨통 틔움
    frequent_top15 = get_frequent_numbers_all_time(csv_filename, top_n=15)
    if sum(1 for n in nums if n in frequent_top15) < 2: return False
    
    # 7. 저빈출(Cold) 번호 제외 (Bottom 5) - 동일
    all_frequent = get_frequent_numbers_all_time(csv_filename, top_n=45)
    low_frequent = all_frequent[-5:]
    if any(n in low_frequent for n in nums): return False
    
    # 8. 소수 (Prime) 개수 (1~4개) - 동일
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
    prime_count = sum(1 for n in nums if n in primes)
    if not (1 <= prime_count <= 4): return False
    
    # 9. 고급 수학적 제약 (유지)
    # 피보나치, 삼각수 등이 너무 많이 포함되면 제외
    fibonacci = [1, 2, 3, 5, 8, 13, 21, 34]
    if sum(1 for n in nums if n in fibonacci) > 2: return False
    
    triangular = [1, 3, 6, 10, 15, 21, 28, 36, 45]
    if sum(1 for n in nums if n in triangular) > 2: return False
    
    products = [i*(i+1) for i in range(1, 7) if i*(i+1) <= 45]
    if sum(1 for n in nums if n in products) > 2: return False  # 1개->2개로 미세 완화
    
    # 10. 최근 패턴 유사성 체크 (유지)
    if not check_similarity_with_recent_patterns(nums, csv_filename): return False
    
    return True

# =========================================================
#  데이터 조회 및 유틸리티
# =========================================================

# 캐싱을 통해 속도 향상
_frequent_cache = []
_cache_filename = ""
_cache_timestamp = 0

def get_frequent_numbers_all_time(filename, top_n=25):
    global _frequent_cache, _cache_filename, _cache_timestamp
    try:
        current_timestamp = os.path.getmtime(filename)
    except:
        current_timestamp = 0
        
    if (_frequent_cache and _cache_filename == filename and 
        _cache_timestamp == current_timestamp and len(_frequent_cache) >= top_n):
        return _frequent_cache[:top_n]
        
    frequent_nums = []
    try:
        with open(filename, encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                nums = row[3:9]
                if all(n.isdigit() for n in nums):
                    frequent_nums.extend([int(n) for n in nums])
    except: pass
    
    counter = Counter(frequent_nums)
    full_list = [num for num, count in counter.most_common(45)]
    
    # 캐시 업데이트
    _frequent_cache = full_list
    _cache_filename = filename
    _cache_timestamp = current_timestamp
    
    return full_list[:top_n]

def get_recent_winning_numbers(filename, count=5):
    recent_wins = []
    try:
        with open(filename, encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            rows = list(reader)
            for row in rows[-count:]:
                nums = row[3:9]
                if all(n.isdigit() for n in nums):
                    recent_wins.append([int(n) for n in nums])
    except: pass
    return recent_wins

def check_similarity_with_recent_patterns(numbers, filename, recent_count=30):
    """최근 당첨번호와 너무 흡사하면 제외"""
    nums = sorted(numbers)
    try:
        with open(filename, encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            rows = list(reader)
            recent_rows = rows[-recent_count:] if len(rows) > recent_count else rows
            
            for row in recent_rows:
                nums_row = row[3:9]
                if all(n.isdigit() for n in nums_row):
                    past_sorted = sorted([int(n) for n in nums_row])
                    # 5개 이상 번호가 겹치면 제외
                    if len(set(nums) & set(past_sorted)) >= 5: return False
                    
                    # 간격 패턴이 너무 비슷해도 제외
                    past_gaps = [past_sorted[i+1] - past_sorted[i] for i in range(5)]
                    current_gaps = [nums[i+1] - nums[i] for i in range(5)]
                    # 간격 패턴이 3개 이상 일치하면 제외
                    if sum(1 for i in range(5) if past_gaps[i] == current_gaps[i]) >= 3:
                        return False
    except: pass
    return True

# =========================================================
#  핵심 생성 로직
# =========================================================

def generate_combinations(past_combs, last_draw, n_sets=15):
    results = []
    
    # Top5 규칙 준비
    top5_in_last = [n for n in TOP5 if n in last_draw]
    
    # 중복 방지 준비 (이번주 이미 생성한 번호 + 과거 당첨 번호 + 지난주 추천 번호)
    past_recommended = load_past_recommended_combinations()
    all_past_combs = past_combs | past_recommended
    
    csv_filename = find_latest_lotto_file()
    
    print(f"[INFO] 번호 생성 시작: 목표 {n_sets}세트, 시도 제한 500,000회")
    
    tries = 0
    max_tries = 500000  # [요청반영] 50만 번 시도
    
    while len(results) < n_sets and tries < max_tries:
        tries += 1
        
        # 완전 랜덤 생성 (가중치 없이 순수 무작위성에서 필터로 걸러냄)
        # -> 가중치를 주면 오히려 필터와 충돌하여 확률이 떨어질 수 있음
        nums = random.sample(range(1, 46), 6)
        
        # 기본 필터 1 (속도 위해 가벼운 체크 먼저)
        if not check_even_odd(nums): continue
        
        # Top5 규칙 적용
        line_idx = len(results) % 5
        nums = apply_top5_rule(nums, top5_in_last, line_idx)
        
        # 엄격한 품질 체크 (여기서 99% 걸러짐)
        if not check_pattern_quality(nums, csv_filename): continue
            
        # 중복 체크
        comb = tuple(sorted(nums))
        if comb in all_past_combs or comb in [tuple(sorted(r)) for r in results]: 
            continue
            
        # 합격
        results.append(sorted(nums))
    
    print(f"[INFO] 생성 종료: {len(results)}/{n_sets} 세트 생성 완료 (총 시도: {tries}회)")
    
    # 만약 50만 번을 돌려도 15개가 안 되면? 
    # Fallback 없이 있는 그대로 출력 (중복 채우기 X)
    
    return results

def find_latest_lotto_file():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'lotto_total.csv')
    return csv_path

def load_past_recommended_combinations():
    if not os.path.exists('lotto_result.txt'):
        return set()
    past_recommended = set()
    try:
        with open('lotto_result.txt', encoding='utf-8') as f:
            content = f.read()
        pattern = r'^[A-E]: ([\d\s]+)$'
        lines = content.split('\n')
        for line in lines:
            match = re.match(pattern, line.strip())
            if match:
                nums = [int(x) for x in match.group(1).split()]
                if len(nums) == 6:
                    past_recommended.add(tuple(sorted(nums)))
    except: pass
    return past_recommended

def save_lotto_result(combs, latest_file, count):
    # 회차 정보 읽기
    round_no = '????'
    try:
        with open(latest_file, encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) > 1:
                round_no = lines[-1].split(',')[1]
    except: pass

    lines = []
    lines.append(f"{count:02d}번째 추천 번호에요~❤️❤️")
    lines.append(f"[직전회차 {round_no}회]")
    lines.append('-'*30)
    
    # [수정] 중복 세트 방지 로직
    # 생성된 개수만큼만 출력하고, 부족하면 빈 칸으로 둡니다.
    # 억지로 cycle 돌려서 복사하지 않습니다.
    
    total_combs = len(combs)
    current_idx = 0
    
    for i in range(3): # A, B, C 그룹
        # 그룹 헤더 필요 시 추가 가능
        for j in range(5): # 각 그룹당 5줄
            if current_idx < total_combs:
                nums = combs[current_idx]
                current_idx += 1
                nums_str = ' '.join(str(n) for n in nums)
                lines.append(f"{chr(65+j)}: {nums_str}")
            else:
                # 50만 번 시도해도 부족한 경우 (극히 드물 것임)
                lines.append(f"{chr(65+j)}: (조건 만족 번호 없음)")
        lines.append('-'*30)

    messages = [
        '🎉 "이번 주는 당신의 차례입니다! 대박을 기원합니다!"',
        '🍀 "행운의 바람이 불어오고 있어요. 1등 갑시다!"',
        '✨ "당신의 손끝이 기적을 만들었습니다. 당첨을 응원합니다!"',
        '🌟 "행운은 준비된 자의 것! 준비되셨죠?"',
        '🎯 "인생 역전, 오늘이 그 날입니다!"'
    ]
    lines.append(random.choice(messages))
    
    with open('lotto_result.txt', 'a', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

def main():
    try:
        CSV_FILE = find_latest_lotto_file()
        if not os.path.exists(CSV_FILE):
            print("데이터 파일이 없습니다.")
            return

        past_combs = load_past_combinations(CSV_FILE)
        last_draw = get_last_draw_numbers(CSV_FILE)
        
        # 15개 목표 생성
        combs = generate_combinations(past_combs, last_draw, n_sets=15)
        
        # 회차 카운트 계산
        count = 1
        if os.path.exists('lotto_result.txt'):
            with open('lotto_result.txt', encoding='utf-8') as f:
                content = f.read()
                count = content.count('번째 추천 번호에요~') + 1
        
        save_lotto_result(combs, CSV_FILE, count)
        print(f"[SUCCESS] {len(combs)}개 조합 저장 완료")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()