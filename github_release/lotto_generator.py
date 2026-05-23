"""
===============================================================================
        대한민국 동행복권 로또6/45 추천번호 생성 시스템
===============================================================================

이 시스템은 대한민국 로또6/45의 전 회차 당첨번호 데이터를 기반으로,
다양한 통계적·수학적 제약 조건과 중복 방지, 빈출번호 활용, 부분 일치 조합 등
실제 코드에 구현된 로직에 따라 번호를 추천합니다.
(순수하게 재미로 만든 코드이며 실제 당첨 보장과는 무관합니다.)

흥미로운 논리가 있다면 추가해 주세요~~

[주요 단계 및 실제 적용 제약 조건]

1. 기본 구조
   - 각 구간(1~15, 16~30, 31~45)에 1~3개씩 번호 포함
   - 전체가 홀수 또는 전체가 짝수인 조합은 제외
   - 4개 이상 연속된 숫자 금지 (3개 연속은 허용)
   - 끝수(1의 자리) 중복 4개 이상 금지 (3개까지 허용)

2. 통계적 한정
   - 번호 합계: 145~165
   - 분산: 80~250
   - 같은 십의자리(10, 20, 30, 40) 3개 이상 집중 금지
   - 0, 5로 끝나는 수는 최대 1개

3. 빈출/저빈출 번호 활용
   - 전체 데이터 기준 상위 12개 빈출번호 중 최소 2개 포함
   - 하위 5개 저빈출번호는 완전 배제
   - 50% 확률로 상위 20개 빈출번호에서 3~5개 우선 선택

4. 수학적 패턴 고려
   - 소수: 1~4개 포함
   - 제곱수: 최대 1개
   - 5의 배수: 최대 1개
   - 같은 간격(차이)이 2번 이상 반복 금지

5. 고급 수학적 논리 고려
   - 피보나치수: 최대 2개
   - 삼각수: 최대 2개
   - 연속수 곱: 최대 1개
   - 등차수열(같은 차이로 연속): 4개 이상 금지
   - 자릿수합: 같은 합 3개 이상 금지
   - 대칭쌍(1↔45, 2↔44 등): 1개 이상 금지

6. 최근 당첨 패턴 유사성 배제
   - 최근 30회차와 5개 이상 일치 금지
   - 최근 30회차와 간격 패턴 3개 이상 일치 금지

7. 중복 방지
   - 과거 모든 당첨번호, 추천번호, 현재 세트 내 중복 조합 완전 배제

8. Top5 특별규칙 및 3등/4등 특화
   - 빈출번호 Top5([1,3,7,12,13])와 직전회차 교집합에 따라 일부 번호 강제 포함
   - 최근 3회차 당첨번호와 4개 일치하는 조합 직접 생성
   - 빈출번호 기반 클러스터링(여러 조합에 공통 번호 배치)

[기타]
- 모든 추천/분석은 최신 csv 데이터 파일을 기반으로 동작
- 랜덤성, 데이터 상황, 중복 방지 등으로 인해 일부 조건은 시도 횟수 내에서 최대한 충족
- 기대 효과: 4등/3등 당첨 확률이 통계적으로 소폭 향상될 수 있음(실제 당첨 보장 아님)

===============================================================================
"""

import csv
import random
from collections import Counter
import os
import re
import datetime

# 고정 Top5 번호
TOP5 = [1, 3, 7, 12, 13]

# 구간 정의
RANGES = [(1, 15), (16, 30), (31, 45)]

# 과거 당첨 조합 집합 생성
def load_past_combinations(filename):
    past = set()
    with open(filename, encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # 헤더
        for row in reader:
            nums = row[3:9]
            if all(n.isdigit() for n in nums):
                comb = tuple(sorted(int(n) for n in nums))
                past.add(comb)
    return past

# 직전 회차 당첨번호 추출
def get_last_draw_numbers(filename):
    with open(filename, encoding='utf-8') as f:
        lines = f.readlines()
        for line in reversed(lines):
            row = line.strip().split(',')
            nums = row[3:9]
            if all(n.isdigit() for n in nums):
                return [int(n) for n in nums]
    return []

# 구간별 번호풀 생성
def get_number_pools():
    pools = []
    for start, end in RANGES:
        pools.append(list(range(start, end+1)))
    return pools

# 홀짝 비율 체크
def check_even_odd(numbers):
    odds = sum(1 for n in numbers if n % 2)
    evens = 6 - odds
    return (odds, evens) in [(3,3), (4,2), (2,4)]

# 구간 분포 체크
def check_ranges(numbers):
    counts = [0, 0, 0]
    for n in numbers:
        for i, (start, end) in enumerate(RANGES):
            if start <= n <= end:
                counts[i] += 1
    return counts == [2,2,2]

# 2연속 한 쌍, 3연속 불가 체크
def check_consecutive(numbers):
    nums = sorted(numbers)
    cons = []
    i = 0
    while i < 5:
        if nums[i+1] - nums[i] == 1:
            # 연속 시작
            cnt = 2
            while i+cnt < 6 and nums[i+cnt] - nums[i+cnt-1] == 1:
                cnt += 1
            cons.append(cnt)
            i += cnt
        else:
            i += 1
    return cons.count(2) == 1 and all(c < 3 for c in cons)

# 끝수 2개만 일치(3개 이상 불가)
def check_last_digit(numbers):
    last_digits = [n % 10 for n in numbers]
    counter = Counter(last_digits)
    return list(counter.values()).count(2) == 1 and max(counter.values()) < 3

# 합계 체크
def check_sum(numbers):
    return 140 <= sum(numbers) <= 170

# Top5 포함 규칙 적용
def apply_top5_rule(draw, top5_in_last, line_idx):
    # draw: 현재 조합, top5_in_last: 직전회차와 top5 교집합, line_idx: 0~4
    if len(top5_in_last) >= 2:
        if line_idx == 0:
            for n in top5_in_last[:2]:
                if n not in draw:
                    draw[0] = n
                    draw[1] = top5_in_last[1]
        elif line_idx == 1:
            if top5_in_last[0] not in draw:
                draw[0] = top5_in_last[0]
        elif line_idx == 2:
            if top5_in_last[1] not in draw:
                draw[0] = top5_in_last[1]
    elif len(top5_in_last) == 1:
        if line_idx == 0 and top5_in_last[0] not in draw:
            draw[0] = top5_in_last[0]
    # 0개면 적용 안 함
    return draw

# 조합 생성 함수 (3등/4등 확률 개선 버전)
def generate_combinations(past_combs, last_draw, n_sets=15):
    """
    완전 제약 조건 하에서 당첨번호 조합 생성
    7단계(중복 방지), 8단계(Top5 특별규칙) 포함
    """
    results = []
    pools = get_number_pools()
    
    # ==================== 8단계: Top5 특별규칙 준비 ====================
    top5_in_last = [n for n in TOP5 if n in last_draw]
    print(f"[INFO] Top5 규칙: 직전회차와 교집합 {len(top5_in_last)}개 ({top5_in_last})")
    
    # ==================== 7단계: 중복 방지 준비 ====================
    # 7-1. 과거 당첨번호 로드 (1,174개 조합)
    # 7-2. 과거 추천번호 로드 (210개 조합)
    past_recommended = load_past_recommended_combinations()
    all_past_combs = past_combs | past_recommended
    print(f"[INFO] 중복 방지: 과거 당첨 {len(past_combs)}개 + 과거 추천 {len(past_recommended)}개")
    
    # 3등/4등 확률 향상을 위한 데이터 준비 - 전체 데이터 사용으로 개선!
    # CSV_FILE을 함수 내부에서 동적으로 찾기
    csv_filename = find_latest_lotto_file()
    frequent_nums = get_balanced_frequent_numbers(csv_filename, top_n=30)  # 균형잡힌 빈출번호 사용
    recent_wins = get_recent_winning_numbers(csv_filename, count=3)
    
    print(f"[INFO] 분석 완료 - 균형잡힌 빈출번호 {len(frequent_nums)}개, 최근 당첨번호 {len(recent_wins)}회차")
    
    # 1단계: 부분 일치 조합 생성 (4등 확률 향상)
    partial_match_sets = generate_partial_match_sets(recent_wins, frequent_nums, target_match=4)
    for combo in partial_match_sets:
        if len(results) < n_sets:
            results.append(combo)
    
    print(f"[INFO] 부분 일치 조합 생성: {len(partial_match_sets)}개")
    
    # 2단계: 기존 로직으로 나머지 조합 생성
    tries = 0
    quality_failures = 0
    duplicate_failures = 0
    
    # 더 유연한 생성을 위해 시도 횟수 증가 및 단계별 완화
    max_tries = 50000  # 시도 횟수
    
    while len(results) < n_sets and tries < max_tries:
        tries += 1
        
        # ==================== 3단계: 빈출번호 기반 가중 선택 ====================
        # 빈출번호 우선 사용 (50% 확률로 증가 - 전체 데이터 기반이므로 더 신뢰도 높음)
        if random.random() < 0.5 and frequent_nums:
            # 상위 빈출번호에서 3-5개 선택 (확률 조정)
            base_count = random.randint(3, 5)
            # 상위 20개 빈출번호에서 선택 (더 넓은 범위)
            nums = random.sample(frequent_nums[:20], min(base_count, len(frequent_nums)))
            
            # 나머지는 전체 범위에서 선택
            remaining_pool = [i for i in range(1, 46) if i not in nums]
            nums.extend(random.sample(remaining_pool, 6 - len(nums)))
        else:
            # ==================== 1단계: 기본 구조 생성 ====================
            # 구간별 선택 (각 구간에서 2개씩)
            nums = []
            for pool in pools:
                nums += random.sample(pool, 2)
            random.shuffle(nums)
        
        # 기본 홀짝 체크 (1단계-2에서 더 엄격하게 체크됨)
        if not check_even_odd(nums):
            continue
            
        # ==================== 8단계: Top5 특별규칙 적용 ====================
        line_idx = len(results) % 5  # 0~4 라인별 차별화
        nums = apply_top5_rule(nums, top5_in_last, line_idx)
        
        # ==================== 1~6단계: 완전 제약 조건 체크 ====================
        if not check_pattern_quality(nums, csv_filename):
            quality_failures += 1
            continue
            
        # ==================== 7단계: 중복 방지 최종 체크 ====================
        comb = tuple(sorted(nums))
        
        # 7-1. 과거 당첨번호와 중복 체크
        # 7-2. 과거 추천번호와 중복 체크  
        # 7-3. 현재 세트 내 실시간 중복 체크
        if comb in all_past_combs or comb in [tuple(sorted(r)) for r in results]:
            duplicate_failures += 1
            continue
            
        results.append(nums[:])
    
    # 3단계: 스마트 클러스터링 적용 (공통 번호 배치)
    results = apply_smart_clustering(results, cluster_size=5)
    
    print(f"[INFO] 생성 완료: {len(results)}개 조합")
    print(f"[INFO] 총 시도: {tries}회 (품질 실패: {quality_failures}회, 중복 실패: {duplicate_failures}회)")
    print(f"[INFO] 8단계 완전 제약 조건 적용 및 클러스터링 완료")
    return results

def find_latest_lotto_file():
    files = os.listdir('.')
    lotto_files = []
    for f in files:
        m = re.match(r'lotto_(\d+)\.csv$', f)
        if m:
            lotto_files.append((int(m.group(1)), f))
    if not lotto_files:
        raise FileNotFoundError('lotto_*.csv 파일이 없습니다.')
    lotto_files.sort(reverse=True)
    return lotto_files[0][1]

def save_lotto_result(combs, latest_file, count):
    import random  # 함수 시작 부분에 import 추가
    # latest_file에서 회차 추출
    m = re.search(r'lotto_(\d+)\.csv', latest_file)
    round_no = m.group(1) if m else '????'
    lines = []
    lines.append(f"{count:02d}번째 추천 번호에요~❤️❤️")
    lines.append(f"[직전회차 {round_no}회]")
    lines.append('-'*30)
    
    # 안전한 조합 출력 (생성된 조합 수에 맞춰 동적 처리)
    available_combs = len(combs)
    print(f"[INFO] 사용 가능한 조합 수: {available_combs}개")
    
    if available_combs == 0:
        print("[ERROR] 생성된 조합이 없습니다!")
        return
    
    for i in range(3):
        for j in range(5):
            combo_idx = i * 5 + j
            if combo_idx < available_combs:
                # 정상적으로 생성된 조합 사용
                nums = sorted(combs[combo_idx])
            else:
                # 부족한 조합은 기존 조합을 순환하여 사용
                cycle_idx = combo_idx % available_combs
                nums = sorted(combs[cycle_idx])
            
            # 안전한 번호 검증 및 수정
            if len(set(nums)) != 6:
                print(f"[WARNING] 중복 번호 발견: {nums}")
                # 중복 제거 후 부족한 번호 추가
                unique_nums = list(set(nums))
                missing_count = 6 - len(unique_nums)
                available_nums = [n for n in range(1, 46) if n not in unique_nums]
                if len(available_nums) >= missing_count:
                    additional_nums = random.sample(available_nums, missing_count)
                    nums = sorted(unique_nums + additional_nums)
                else:
                    # 완전 실패시 기본 조합 사용
                    print(f"[ERROR] 중복 수정 실패, 기본 조합 사용")
                    nums = sorted([1, 7, 14, 21, 28, 35])  # 기본 안전 조합
            
            nums_str = ' '.join(str(n) for n in nums)
            lines.append(f"{chr(65+j)}: {nums_str}")
        lines.append('-'*30)
    messages = [
        '🎉 "이번 주는 당신의 차례입니다! 대박을 기원합니다!"',
        '🍀 "행운의 바람이 불어오고 있어요. 1등 갑시다!"',
        '✨ "당신의 손끝이 기적을 만들었습니다. 당첨을 응원합니다!"',
        '🌟 "행운은 준비된 자의 것! 준비되셨죠?"',
        '🎯 "인생 역전, 오늘이 그 날입니다!"',
        '🤑 "다음 주 당첨자 인터뷰, 바로 당신입니다!"',
        '💸 "지금 이 번호… 뭔가 다릅니다. 대박의 예감!"',
        '🚀 "꿈은 이뤄진다! 이번엔 현실로!"',
        '🔥 "오늘 찍은 번호, 불타는 운명을 안고 있습니다!"',
        '🌈 "무지개 끝에 황금이 있다면, 당신의 손에 로또가 있습니다!"',
        '🧲 "행운을 끌어당기는 자석이 되어 드립니다!"',
        '🕊️ "간절함은 통합니다. 간절히 바라면 이루어질 거예요."',
        '🛫 "당첨의 여정, 지금 시작됩니다. 착륙지는 1등!"',
        '🍀 "복권의 신이 미소 지었습니다. 바로 당신에게!"',
        '🎁 "선물 같은 번호, 선물 같은 당첨을 기원합니다!"',
        '🌌 "우주는 지금 당신에게 속삭입니다… 이번 주야…"',
        '🧧 "이번 주, 복(福)은 당신의 차지입니다!"',
        '🙌 "이 번호, 그냥 좋다… 느낌이 온다!"',
        '💫 "소름 돋는 예감, 이번엔 진짜다!"',
        '🧿 "당첨을 막는 모든 불운을 차단했습니다. 가즈아~!"'
    ]
    lines.append(random.choice(messages))
    with open('lotto_result.txt', 'a', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

# 과거 추천번호 조합도 로드하여 중복 방지
def load_past_recommended_combinations():
    """과거 추천번호들을 로드하여 중복 방지"""
    if not os.path.exists('lotto_result.txt'):
        return set()
    
    import re
    past_recommended = set()
    
    with open('lotto_result.txt', encoding='utf-8') as f:
        content = f.read()
    
    # A~E 라인의 번호들 추출
    pattern = r'^[A-E]: ([\d\s]+)$'
    lines = content.split('\n')
    
    for line in lines:
        match = re.match(pattern, line.strip())
        if match:
            nums = [int(x) for x in match.group(1).split()]
            if len(nums) == 6:
                comb = tuple(sorted(nums))
                past_recommended.add(comb)
    
    return past_recommended

# 과거 패턴 유사성 체크를 위한 함수
def check_similarity_with_recent_patterns(numbers, filename, recent_count=30):
    """최근 당첨번호들과의 유사성이 너무 높으면 제외"""
    nums = sorted(numbers)
    
    try:
        with open(filename, encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # 헤더
            rows = list(reader)
            
            # 최근 30회차만 확인
            recent_rows = rows[-recent_count:] if len(rows) > recent_count else rows
            
            for row in recent_rows:
                past_nums = row[3:9]  # 당첨번호 6개
                if all(n.isdigit() for n in past_nums):
                    past_sorted = sorted([int(n) for n in past_nums])
                    
                    # 5개 이상 일치하면 너무 유사
                    matches = len(set(nums) & set(past_sorted))
                    if matches >= 5:
                        return False
                    
                    # 패턴 유사성 체크 (간격 패턴이 비슷하면 제외)
                    past_gaps = [past_sorted[i+1] - past_sorted[i] for i in range(5)]
                    current_gaps = [nums[i+1] - nums[i] for i in range(5)]
                    
                    # 간격 패턴이 3개 이상 같으면 제외
                    gap_matches = sum(1 for i in range(5) if past_gaps[i] == current_gaps[i])
                    if gap_matches >= 3:
                        return False
    except:
        pass  # 파일 오류 시 패스
    
    return True

# 고급 수학적 제약 조건들
def check_advanced_mathematical_constraints(numbers):
    """
    5단계: 고급 수학적 제약 조건들
    피보나치수, 삼각수, 연속수곱, 등차수열, 자릿수합, 대칭성 체크
    """
    nums = sorted(numbers)
    from collections import Counter
    
    # 5-1. 피보나치수 제한 (최대 2개)
    fibonacci_45 = [1, 2, 3, 5, 8, 13, 21, 34]  # 45 이하 피보나치 수
    fib_count = sum(1 for n in nums if n in fibonacci_45)
    if fib_count > 2:
        return False
    
    # 5-2. 삼각수 제한 (최대 2개)
    triangular_nums = [1, 3, 6, 10, 15, 21, 28, 36, 45]  # 45 이하 삼각수
    triangular_count = sum(1 for n in nums if n in triangular_nums)
    if triangular_count > 2:
        return False
    
    # 5-3. 연속수 곱 제한 (최대 1개)
    products_in_range = []
    for i in range(1, 7):  # 1*2=2, 2*3=6, ..., 6*7=42
        if i * (i + 1) <= 45:
            products_in_range.append(i * (i + 1))
    
    product_count = sum(1 for n in nums if n in products_in_range)
    if product_count > 1:
        return False
    
    # 5-4. 등차수열 제한 (4개 이상 연속 등차수열 금지)
    for i in range(len(nums) - 2):
        if nums[i+1] - nums[i] == nums[i+2] - nums[i+1]:
            # 등차수열 3개 발견시 더 체크
            consecutive_arithmetic = 3
            for j in range(i+3, len(nums)):
                if nums[j] - nums[j-1] == nums[i+1] - nums[i]:
                    consecutive_arithmetic += 1
                else:
                    break
            if consecutive_arithmetic >= 4:
                return False
    
    # 5-5. 자릿수 합 제한 (같은 자릿수합 3개 이상 금지)
    digit_sums = []
    for n in nums:
        digit_sum = sum(int(d) for d in str(n))
        digit_sums.append(digit_sum)
    
    digit_sum_counts = Counter(digit_sums)
    if max(digit_sum_counts.values()) >= 3:
        return False
    
    # 5-6. 대칭성 체크 (1↔45, 2↔44 등의 대칭쌍 1개 이상 금지)
    symmetric_pairs = 0
    for n in nums:
        if (46 - n) in nums and n < 23:  # 중심값 23 미만에서만 체크
            symmetric_pairs += 1
    if symmetric_pairs >= 1:
        return False
    
    return True

# 기존 check_pattern_quality 함수 수정
def check_pattern_quality(numbers, csv_filename):
    """
    완전 제약 조건 하에서 번호 조합의 패턴 품질을 체크
    8단계 체계적 검증 프로세스
    """
    nums = sorted(numbers)
    
    # ==================== 1단계: 기본 구조 생성 검증 ====================
    
    # 1-1. 구간별 분배 체크 (각 구간에 정확히 2개씩 → 완화: 최소 1개, 최대 3개)
    ranges = [(1, 15), (16, 30), (31, 45)]
    for i, (start, end) in enumerate(ranges):
        count = sum(1 for n in nums if start <= n <= end)
        if count < 1 or count > 3:  # 완화: 각 구간에 1~3개 허용
            return False
    
    # 1-2. 홀짝 균형 (전체 홀수 또는 전체 짝수 조합 완전 배제)
    odds = sum(1 for n in nums if n % 2)
    if odds == 0 or odds == 6:  # 모두 홀수 또는 모두 짝수 금지
        return False
    
    # 1-3. 연속번호 제한 (완화: 3개 이상 연속 금지, 연속쌍 개수는 자유)
    consecutive = 1
    max_consecutive = 1
    
    for i in range(1, len(nums)):
        if nums[i] - nums[i-1] == 1:
            consecutive += 1
            max_consecutive = max(max_consecutive, consecutive)
        else:
            consecutive = 1
    
    if max_consecutive >= 4:  # 완화: 4개 이상 연속만 금지 (3개 연속은 허용)
        return False
    
    # 1-4. 끝수 중복 제한 (완화: 4개 이상만 금지)
    last_digits = [n % 10 for n in nums]
    from collections import Counter
    digit_counts = Counter(last_digits)
    
    if max(digit_counts.values()) >= 4:  # 완화: 4개 이상만 금지 (3개까지 허용)
        return False
    
    # ==================== 2단계: 통계적 제약 ====================
    
    # 2-1. 합계 범위 (145~165, 20점 엄격 범위)
    total = sum(nums)
    if total < 145 or total > 165:
        return False
    
    # 2-2. 분산값 제한 (80~250)
    import statistics
    variance = statistics.variance(nums)
    if variance < 80 or variance > 250:
        return False
    
    # 2-3. 첫째자리 균형 (같은 십의자리에 3개 이상 집중 금지)
    first_digits = [n // 10 for n in nums]
    first_digit_counts = Counter(first_digits)
    if max(first_digit_counts.values()) >= 3:
        return False
    
    # 2-4. 끝수 특별제한 (0,5로 끝나는 수 최대 1개)
    ending_0_5 = sum(1 for n in nums if n % 10 in [0, 5])
    if ending_0_5 > 1:
        return False
    
    # ==================== 3단계: 빈출번호 기반 필터링 ====================
    
    # 3-1. 의무 포함 (전체1174회차 상위12개 빈출번호 중 최소 2개 포함으로 완화)
    frequent_top12 = get_frequent_numbers_all_time(csv_filename, top_n=12)
    frequent_count = sum(1 for n in nums if n in frequent_top12)
    if frequent_count < 2:  # 완화: 최소 2개 (기존 3개에서 2개로)
        return False
    
    # 3-2. 완전 배제 (전체1174회차 하위8개 저빈출번호 완전 제외 → 완화: 하위5개만)
    all_frequent = get_frequent_numbers_all_time(csv_filename, top_n=45)
    low_frequent = all_frequent[-5:]  # 완화: 하위 5개 (기존 8개에서 5개로)
    low_frequent_count = sum(1 for n in nums if n in low_frequent)
    if low_frequent_count > 0:  # 저빈출번호 완전 제외
        return False
    
    # ==================== 4단계: 수학적 패턴 제약 ====================
    
    # 4-1. 소수 제한 (1~4개로 완화)
    primes_1_45 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
    prime_count = sum(1 for n in nums if n in primes_1_45)
    if prime_count < 1 or prime_count > 4:  # 완화: 1~4개 (기존 2~3개에서)
        return False
    
    # 4-2. 제곱수 제한 (최대 1개)
    squares = [1, 4, 9, 16, 25, 36]  # 1~45 범위의 제곱수
    square_count = sum(1 for n in nums if n in squares)
    if square_count > 1:
        return False
    
    # 4-3. 5의 배수 제한 (최대 1개)
    multiples_of_5 = [5, 10, 15, 20, 25, 30, 35, 40, 45]
    multiple_5_count = sum(1 for n in nums if n in multiples_of_5)
    if multiple_5_count > 1:
        return False
    
    # 4-4. 간격 패턴 (같은 간격이 2번 이상 나오면 배제)
    gaps = [nums[i+1] - nums[i] for i in range(5)]
    gap_counts = Counter(gaps)
    if max(gap_counts.values()) >= 2:
        return False
    
    # ==================== 5단계: 고급 수학적 제약 ====================
    
    if not check_advanced_mathematical_constraints(nums):
        return False
    
    # ==================== 6단계: 패턴 유사성 배제 ====================
    
    if not check_similarity_with_recent_patterns(nums, csv_filename):
        return False
    
    # ==================== 7단계: 중복 방지는 generate_combinations에서 처리 ====================
    # (과거 당첨번호, 과거 추천번호, 실시간 중복은 메인 생성 로직에서 체크)
    
    # ==================== 8단계: Top5 특별규칙은 generate_combinations에서 처리 ====================
    # (Top5 규칙은 메인 생성 로직에서 적용)
    
    return True

# 추가 제약 조건을 위한 전역 변수 캐시
_frequent_cache = []
_cache_filename = ""
_cache_timestamp = 0

def get_frequent_numbers_all_time(filename, top_n=25):
    """전체 회차에서 자주 나오는 번호들 추출 (더 정확한 통계) - 캐시 기능 추가"""
    global _frequent_cache, _cache_filename, _cache_timestamp
    
    # 파일 변경 감지를 위한 타임스탬프 체크
    import os
    try:
        current_timestamp = os.path.getmtime(filename)
    except OSError:
        current_timestamp = 0
    
    # 캐시 유효성 체크 (파일명과 타임스탬프 모두 확인)
    cache_valid = (len(_frequent_cache) > 0 and 
                   _cache_filename == filename and 
                   _cache_timestamp == current_timestamp and
                   len(_frequent_cache) >= top_n)
    
    if cache_valid:
        return _frequent_cache[:top_n]
    
    from collections import Counter
    
    frequent_nums = []
    total_rounds = 0
    
    with open(filename, encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # 헤더
        
        for row in reader:
            nums = row[3:9]  # 당첨번호 6개
            if all(n.isdigit() for n in nums):
                frequent_nums.extend([int(n) for n in nums])
                total_rounds += 1
    
    # 빈도순으로 정렬하여 상위 번호들 반환
    counter = Counter(frequent_nums)
    print(f"[INFO] 전체 {total_rounds}회차 데이터 분석 완료 (총 {len(frequent_nums)}개 번호)")
    
    # 상위 빈출번호들과 그 출현 횟수 출력
    top_frequent = counter.most_common(45)  # 전체 저장
    print(f"[INFO] 상위 10개 빈출번호: {[(num, count) for num, count in top_frequent[:10]]}")
    
    # 캐시에 저장 (파일명과 타임스탬프도 함께 저장)
    _frequent_cache = [num for num, count in top_frequent]
    _cache_filename = filename
    _cache_timestamp = current_timestamp
    
    print(f"[INFO] 캐시 갱신: {len(_frequent_cache)}개 빈출번호 데이터 저장 (파일: {filename})")
    return _frequent_cache[:top_n]

def get_frequent_numbers(filename, recent_rounds=50, top_n=25):
    """최근 회차에서 자주 나오는 번호들 추출 (트렌드 분석용)"""
    from collections import Counter
    
    frequent_nums = []
    with open(filename, encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # 헤더
        rows = list(reader)
        
        # 최근 회차만 분석
        recent_rows = rows[-recent_rounds:] if len(rows) > recent_rounds else rows
        
        for row in recent_rows:
            nums = row[3:9]  # 당첨번호 6개
            if all(n.isdigit() for n in nums):
                frequent_nums.extend([int(n) for n in nums])
    
    # 빈도순으로 정렬하여 상위 번호들 반환
    counter = Counter(frequent_nums)
    print(f"[INFO] 최근 {len(recent_rows)}회차 트렌드 분석 완료")
    return [num for num, count in counter.most_common(top_n)]

def get_balanced_frequent_numbers(filename, top_n=30):
    """전체 데이터(70%)와 최근 트렌드(30%)를 조합한 균형잡힌 빈출번호 추출"""
    # 전체 데이터에서 빈출번호 (가중치 70%)
    all_time_frequent = get_frequent_numbers_all_time(filename, top_n)
    
    # 최근 트렌드 빈출번호 (가중치 30%)
    recent_frequent = get_frequent_numbers(filename, recent_rounds=100, top_n=top_n)
    
    # 두 리스트를 점수 기반으로 조합
    from collections import defaultdict
    scores = defaultdict(int)
    
    # 전체 데이터 점수 (순위가 높을수록 높은 점수)
    for i, num in enumerate(all_time_frequent):
        scores[num] += int((top_n - i) * 0.7)  # 70% 가중치, int로 변환
    
    # 최근 트렌드 점수
    for i, num in enumerate(recent_frequent):
        scores[num] += int((top_n - i) * 0.3)  # 30% 가중치, int로 변환
    
    # 점수순으로 정렬
    balanced_frequent = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    result = [num for num, score in balanced_frequent[:top_n]]
    
    print(f"[INFO] 균형잡힌 빈출번호 상위 10개: {result[:10]}")
    return result

def get_recent_winning_numbers(filename, count=5):
    """최근 N회차 당첨번호들 반환"""
    recent_wins = []
    with open(filename, encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # 헤더
        rows = list(reader)
        
        # 최근 count개 회차
        recent_rows = rows[-count:] if len(rows) > count else rows
        
        for row in recent_rows:
            nums = row[3:9]
            if all(n.isdigit() for n in nums):
                recent_wins.append([int(n) for n in nums])
    
    return recent_wins

def generate_partial_match_sets(recent_wins, frequent_nums, target_match=4):
    """과거 당첨번호와 부분 일치하는 조합 생성 - 완화된 조건으로 개선"""
    partial_sets = []
    csv_file = find_latest_lotto_file()
    max_attempts = 50  # 최대 시도 횟수 제한
    
    for win_nums in recent_wins:
        attempts = 0
        generated_for_this_win = 0
        
        # 각 당첨번호마다 최소 1개는 생성하도록 시도
        while generated_for_this_win < 2 and attempts < max_attempts:
            attempts += 1
            
            # target_match를 점진적으로 완화 (4→3→2)
            current_target = max(2, target_match - (attempts // 10))
            base_nums = random.sample(win_nums, min(current_target, len(win_nums)))
            
            # 나머지 자리는 빈출번호에서 채우기
            remaining_count = 6 - len(base_nums)
            available_nums = [n for n in frequent_nums if n not in base_nums]
            
            if len(available_nums) >= remaining_count:
                additional_nums = random.sample(available_nums, remaining_count)
                combination = base_nums + additional_nums
                
                # 완화된 조건으로 체크 (기본 구조만 확인)
                if (check_even_odd(combination) and 
                    check_ranges(combination) and 
                    check_sum(combination) and
                    len(set(combination)) == 6):  # 중복 없는지만 확인
                    
                    partial_sets.append(sorted(combination))
                    generated_for_this_win += 1
                    
                    # 목표 개수 달성하면 조기 종료
                    if len(partial_sets) >= 5:
                        break
        
        # 목표 개수 달성하면 전체 루프 종료
        if len(partial_sets) >= 5:
            break
    
    # 부족하면 간단한 조합으로 채우기
    while len(partial_sets) < 3 and len(frequent_nums) >= 6:
        simple_combination = sorted(random.sample(frequent_nums[:20], 6))
        if (check_even_odd(simple_combination) and 
            check_ranges(simple_combination) and
            simple_combination not in partial_sets):
            partial_sets.append(simple_combination)
    
    return partial_sets[:5]  # 최대 5개까지

def apply_smart_clustering(combinations, cluster_size=3):
    """여러 조합에 공통 번호 배치하여 당첨 확률 향상"""
    if len(combinations) < cluster_size:
        return combinations
    
    # 전체 데이터 기반 빈출번호에서 공통으로 사용할 번호 3-4개 선택
    csv_file = find_latest_lotto_file()
    frequent = get_frequent_numbers_all_time(csv_file, top_n=15)
    common_nums = random.sample(frequent[:10], 3)
    
    print(f"[INFO] 클러스터링용 공통번호: {common_nums}")
    
    # 첫 cluster_size개 조합에 공통 번호 적용
    for i in range(min(cluster_size, len(combinations))):
        current_combination = combinations[i][:]  # 복사본 생성
        
        # 공통 번호를 안전하게 교체
        for common_num in common_nums:
            if common_num not in current_combination:
                # 가장 낮은 빈도의 번호를 찾아서 교체
                replace_idx = 0
                for idx in range(len(current_combination)):
                    if current_combination[idx] not in frequent[:20]:  # 상위 20개에 없는 번호 우선 교체
                        replace_idx = idx
                        break
                
                current_combination[replace_idx] = common_num
        
        # 중복 제거 및 정렬
        current_combination = sorted(list(set(current_combination)))
        
        # 6개가 아니면 부족한 만큼 빈출번호에서 추가
        while len(current_combination) < 6:
            for num in frequent:
                if num not in current_combination:
                    current_combination.append(num)
                    break
        
        # 6개 초과면 랜덤하게 제거
        if len(current_combination) > 6:
            current_combination = sorted(random.sample(current_combination, 6))
        
        combinations[i] = sorted(current_combination)
    
    return combinations

def main():
    """메인 실행 함수 - 안전한 예외 처리와 성능 모니터링 포함"""
    import time
    import sys
    
    start_time = time.time()
    print(f"[INFO] 로또 번호 생성기 시작 - {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. 최신 데이터 파일 찾기
        try:
            CSV_FILE = find_latest_lotto_file()
            print(f"[INFO] 최신 데이터 파일: {CSV_FILE}")
        except FileNotFoundError as e:
            print(f"[ERROR] 로또 데이터 파일을 찾을 수 없습니다: {e}")
            print("[ERROR] lotto_XXXX.csv 형식의 파일이 필요합니다.")
            sys.exit(1)
        
        # 2. 데이터 로드
        try:
            past_combs = load_past_combinations(CSV_FILE)
            last_draw = get_last_draw_numbers(CSV_FILE)
            print(f"[INFO] 데이터 로드 완료 - 과거 조합: {len(past_combs)}개, 직전 회차: {last_draw}")
        except Exception as e:
            print(f"[ERROR] 데이터 로드 실패: {e}")
            sys.exit(1)
        
        # 3. 조합 생성
        try:
            combs = generate_combinations(past_combs, last_draw, n_sets=15)
            if not combs or len(combs) == 0:
                print("[ERROR] 조합 생성 실패 - 생성된 조합이 없습니다.")
                sys.exit(1)
            print(f"[INFO] 조합 생성 성공: {len(combs)}개")
        except Exception as e:
            print(f"[ERROR] 조합 생성 중 오류 발생: {e}")
            sys.exit(1)
        
        # 4. 추천번호 생성 횟수 계산
        count = 1
        if os.path.exists('lotto_result.txt'):
            try:
                with open('lotto_result.txt', encoding='utf-8') as f:
                    content = f.read()
                    # 여러 패턴으로 안전하게 카운팅
                    count_patterns = [
                        '번째 추천 번호에요~',
                        '번째 추천 번호',
                        '추천 번호에요~'
                    ]
                    counts = [content.count(pattern) for pattern in count_patterns]
                    # 가장 높은 카운트 사용 (파일 손상 대비)
                    count = max(counts) + 1 if any(counts) else 1
                    print(f"[INFO] 추천번호 생성 횟수: {count}번째")
            except (UnicodeDecodeError, IOError) as e:
                print(f"[WARNING] lotto_result.txt 읽기 오류: {e}, 기본값 사용")
                count = 1
        
        # 5. 결과 저장
        try:
            save_lotto_result(combs, CSV_FILE, count)
            print(f"[INFO] 결과 저장 완료: lotto_result.txt")
        except Exception as e:
            print(f"[ERROR] 결과 저장 실패: {e}")
            sys.exit(1)
        
        # 6. 성능 및 통계 정보
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"\n{'='*50}")
        print(f"[SUCCESS] 로또 번호 생성 완료!")
        print(f"[STATS] 실행 시간: {execution_time:.2f}초")
        print(f"[STATS] 생성된 조합: {len(combs)}개")
        print(f"[STATS] 추천 횟수: {count}번째")
        print(f"[STATS] 데이터 파일: {CSV_FILE}")
        print(f"[STATS] 완료 시각: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")
        
        return True
        
    except KeyboardInterrupt:
        print(f"\n[WARNING] 사용자에 의해 중단되었습니다.")
        return False
    except Exception as e:
        print(f"[ERROR] 예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1) 