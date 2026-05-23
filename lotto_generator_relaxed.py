"""
실용적 로또 번호 생성기 (합리적 제약 조건 버전)
기존 8단계 중 핵심만 유지하고 나머지는 대폭 완화
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

# 파일명
CSV_FILE = 'lotto_total.csv'

def check_practical_quality(numbers):
    """
    실용적 품질 체크 (핵심 조건만 유지)
    5단계 간소화된 검증 프로세스
    """
    nums = sorted(numbers)
    
    # ==================== 1단계: 기본 구조 (완화) ====================
    
    # 1-1. 구간별 분배 (너무 치우치지 않게만)
    ranges = [(1, 15), (16, 30), (31, 45)]
    for start, end in ranges:
        count = sum(1 for n in nums if start <= n <= end)
        if count > 4:  # 한 구간에 4개 이상 집중되면 배제
            return False
    
    # 1-2. 홀짝 균형 (극단적인 경우만 배제)
    odds = sum(1 for n in nums if n % 2)
    if odds == 0 or odds == 6:  # 모두 홀수 또는 모두 짝수만 금지
        return False
    
    # 1-3. 연속번호 (과도한 연속만 금지)
    consecutive = 1
    max_consecutive = 1
    for i in range(1, len(nums)):
        if nums[i] - nums[i-1] == 1:
            consecutive += 1
            max_consecutive = max(max_consecutive, consecutive)
        else:
            consecutive = 1
    if max_consecutive >= 5:  # 5개 이상 연속만 금지 (4개까지 허용)
        return False
    
    # ==================== 2단계: 합계 범위 (완화) ====================
    total = sum(nums)
    if total < 120 or total > 190:  # 범위 대폭 확대 (120~190)
        return False
    
    # ==================== 3단계: 빈출번호 (대폭 완화) ====================
    # 상위 빈출번호 중 최소 1개만 포함하면 OK
    try:
        frequent_top15 = get_frequent_numbers_all_time(CSV_FILE, top_n=15)
        frequent_count = sum(1 for n in nums if n in frequent_top15)
        if frequent_count < 1:  # 최소 1개만 있으면 OK
            return False
    except:
        pass  # 오류 시 이 조건 무시
    
    # ==================== 4단계: 극단적 패턴만 배제 ====================
    # 제곱수 너무 많으면 배제
    squares = [1, 4, 9, 16, 25, 36]
    square_count = sum(1 for n in nums if n in squares)
    if square_count > 3:  # 3개 이하면 OK
        return False
    
    # ==================== 5단계: 중복 방지는 메인에서 처리 ====================
    
    return True

def get_frequent_numbers_all_time(filename, top_n=25):
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
        # 파일 오류 시 기본값 반환
        return [34, 12, 13, 18, 27, 45, 33, 14, 40, 37, 7, 38, 17, 28, 39]

def load_past_combinations(filename):
    past = set()
    try:
        with open(filename, encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # 헤더
            for row in reader:
                nums = row[3:9]
                if all(n.isdigit() for n in nums):
                    comb = tuple(sorted(int(n) for n in nums))
                    past.add(comb)
    except:
        pass
    return past

def load_past_recommended_combinations():
    """과거 추천번호들을 로드하여 중복 방지"""
    if not os.path.exists('lotto_result.txt'):
        return set()
    
    past_recommended = set()
    try:
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
    except:
        pass
    
    return past_recommended

def generate_practical_combinations(past_combs, n_sets=15):
    """
    실용적 조합 생성 (성공률 높임)
    """
    results = []
    all_past_combs = past_combs | load_past_recommended_combinations()
    frequent_nums = get_frequent_numbers_all_time(CSV_FILE, top_n=20)
    
    print(f"[INFO] 실용적 생성 모드: 중복 방지 {len(all_past_combs)}개")
    print(f"[INFO] 빈출번호 활용: 상위 {len(frequent_nums)}개")
    
    tries = 0
    quality_failures = 0
    duplicate_failures = 0
    
    while len(results) < n_sets and tries < 50000:  # 시도 횟수 조정
        tries += 1
        
        # 70% 확률로 빈출번호 2-4개 사용
        if random.random() < 0.7 and frequent_nums:
            base_count = random.randint(2, 4)
            nums = random.sample(frequent_nums, min(base_count, len(frequent_nums)))
            remaining_pool = [i for i in range(1, 46) if i not in nums]
            nums.extend(random.sample(remaining_pool, 6 - len(nums)))
        else:
            # 구간별 균형 고려한 랜덤 생성
            nums = []
            ranges = [(1, 15), (16, 30), (31, 45)]
            for start, end in ranges:
                count = random.randint(1, 3)  # 각 구간에서 1-3개
                available = [i for i in range(start, end+1) if i not in nums]
                if len(available) >= count:
                    nums.extend(random.sample(available, count))
            
            # 6개가 안 되면 채우기
            while len(nums) < 6:
                remaining = [i for i in range(1, 46) if i not in nums]
                if remaining:
                    nums.append(random.choice(remaining))
                else:
                    break
        
        # 실용적 품질 체크
        if not check_practical_quality(nums):
            quality_failures += 1
            continue
        
        # 중복 방지
        comb = tuple(sorted(nums))
        if comb in all_past_combs or comb in [tuple(sorted(r)) for r in results]:
            duplicate_failures += 1
            continue
        
        results.append(nums[:])
    
    print(f"[INFO] 실용적 생성 완료: {len(results)}개 조합")
    print(f"[INFO] 총 시도: {tries}회 (품질 실패: {quality_failures}회, 중복 실패: {duplicate_failures}회)")
    print(f"[INFO] 성공률: {len(results)/tries*100:.1f}%")
    
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
    # latest_file에서 회차 추출
    m = re.search(r'lotto_(\d+)\.csv', latest_file)
    round_no = m.group(1) if m else '????'
    lines = []
    lines.append(f"{count:02d}번째 추천 번호에요~❤️❤️ (실용모드)")
    lines.append(f"[직전회차 {round_no}회]")
    lines.append('-'*30)
    
    # 안전한 조합 출력
    available_combs = len(combs)
    sets_to_show = min(3, (available_combs + 4) // 5)
    
    combs_used = 0
    for i in range(sets_to_show):
        for j in range(5):
            if combs_used < available_combs:
                nums = sorted(combs[combs_used])
                combs_used += 1
            else:
                # 부족하면 빈출번호 기반으로 생성
                frequent_nums = get_frequent_numbers_all_time(CSV_FILE, top_n=15)
                base_nums = random.sample(frequent_nums[:10], 3)
                remaining = [n for n in range(1, 46) if n not in base_nums]
                base_nums.extend(random.sample(remaining, 3))
                nums = sorted(base_nums)
            
            nums_str = ' '.join(str(n) for n in nums)
            lines.append(f"{chr(65+j)}: {nums_str}")
        lines.append('-'*30)
    
    messages = [
        '🎉 "실용적 분석으로 선별된 번호입니다!"',
        '🍀 "균형잡힌 조합으로 당첨 확률을 높였어요!"',
        '✨ "빈출번호를 적절히 활용한 실전 조합입니다!"',
        '🌟 "현실적이면서도 전략적인 번호 선택!"',
        '🎯 "성공률을 높인 실용적 추천번호!"'
    ]
    lines.append(random.choice(messages))
    
    with open('lotto_result.txt', 'a', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

# 메인 실행 함수
def main():
    try:
        latest_file = find_latest_lotto_file()
        print(f"[INFO] 최신 데이터 파일: {latest_file}")
        
        # 과거 당첨번호 로드
        past_combs = load_past_combinations(latest_file)
        
        # 실용적 조합 생성
        combs = generate_practical_combinations(past_combs, n_sets=15)
        
        if len(combs) >= 15:
            # 결과 저장
            count = 22  # 현재 카운트 조정 필요
            save_lotto_result(combs, latest_file, count)
            print(f"[SUCCESS] {count+1}번째 실용적 추천번호 생성 완료!")
        else:
            print(f"[WARNING] 목표 조합 수 미달성: {len(combs)}/15")
            
    except Exception as e:
        print(f"[ERROR] 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 