import re
import os
from collections import defaultdict
import pandas as pd

# ==========================================
# [설정] 파일 경로 및 CSV 파일명
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOTAL_CSV = "lotto_total.csv"

def get_file_path(filename):
    """현재 스크립트 위치 기준 절대 경로 반환"""
    return os.path.join(BASE_DIR, filename)

def load_lotto_data():
    """lotto_total.csv 파일을 읽어서 DataFrame으로 반환"""
    csv_path = get_file_path(TOTAL_CSV)
    if not os.path.exists(csv_path):
        return None
    
    try:
        # CSV 읽기 (헤더 처리 등 유연하게)
        df = pd.read_csv(csv_path)
        
        # 컬럼명 표준화 (공백 제거 등)
        df.columns = [str(c).strip() for c in df.columns]
        
        # 필수 컬럼 확인 ('회차' 또는 2번째 컬럼)
        # 만약 헤더가 없는 파일이라면? (update_lotto.py 구조에 따라 다름)
        # 보통 헤더가 없다면 첫 줄을 데이터로 인식할 수 있으므로 주의 필요
        # 여기서는 update_lotto.py가 헤더를 포함한다고 가정하거나, 컬럼명을 찾습니다.
        
        target_cols = ['year', 'round', 'date', '1', '2', '3', '4', '5', '6', 'bonus']
        # 만약 컬럼명이 1, 2, 3.. 형태라면 그대로 사용
        
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

def parse_recommendation_history():
    """lotto_result.txt에서 모든 추천번호 기록을 파싱"""
    result_file = get_file_path('lotto_result.txt')
    if not os.path.exists(result_file):
        return []
    
    with open(result_file, encoding='utf-8') as f:
        content = f.read()
    
    blocks = re.split(r'(\d{2})번째 추천 번호에요~[❤️]*', content)
    recommendations = []
    
    # 최신 회차 정보 미리 로드 (추정용)
    df = load_lotto_data()
    latest_round = 1205 # 기본값
    if df is not None:
        try:
            # '회차' 컬럼 찾기 (한글 or 영문 or 인덱스)
            if '회차' in df.columns:
                latest_round = df['회차'].max()
            elif 'round' in df.columns:
                latest_round = df['round'].max()
            else:
                # 컬럼명을 못 찾으면 2번째 컬럼(인덱스 1)을 회차로 가정
                latest_round = df.iloc[:, 1].max()
        except:
            pass

    for i in range(1, len(blocks), 2):
        if i + 1 >= len(blocks):
            break
            
        rec_no = int(blocks[i])
        block = blocks[i + 1]
        
        # 회차 정보 추출
        round_match = re.search(r'\[직전회차 (\d+)회\]', block)
        if round_match:
            round_no = int(round_match.group(1))
            target_round = round_no + 1
        else:
            # 정보 없으면 최신 회차 기준으로 역산 (대략적)
            target_round = latest_round + rec_no - 5 
        
        numbers = []
        lines = block.split('\n')
        current_set = []
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
            line_match = re.match(r'^([A-E]): ([\d\s]+)', line)
            if line_match:
                nums = [int(x) for x in line_match.group(2).split()]
                if len(nums) == 6:
                    current_set.append(nums)
                    if len(current_set) == 5:
                        numbers.extend(current_set)
                        current_set = []
        
        if current_set: numbers.extend(current_set)
        
        if numbers:
            recommendations.append({
                'recommendation_no': rec_no,
                'target_round': target_round,
                'numbers': numbers
            })
    
    return recommendations

def get_winning_numbers(round_no):
    """lotto_total.csv에서 특정 회차 당첨번호 찾기"""
    df = load_lotto_data()
    if df is None: return None
    
    try:
        # 회차 컬럼 식별
        round_col = '회차' if '회차' in df.columns else ('round' if 'round' in df.columns else None)
        
        if round_col:
            round_data = df[df[round_col] == round_no]
        else:
            # 컬럼명이 없으면 2번째 컬럼(인덱스 1)이 회차라고 가정
            round_data = df[df.iloc[:, 1] == round_no]

        if round_data.empty:
            return None
            
        row = round_data.iloc[0]
        
        # 당첨번호 추출 (컬럼명 '1'~'6' 또는 인덱스 3~8)
        winning_nums = []
        # 컬럼명으로 시도
        if '1' in df.columns and '6' in df.columns:
            for k in range(1, 7):
                winning_nums.append(int(row[str(k)]))
        else:
            # 인덱스로 시도 (보통 4번째~9번째가 번호)
            # update_lotto.py: date, round, date, 1, 2, 3, 4, 5, 6, bonus
            # indices: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
            for k in range(3, 9):
                winning_nums.append(int(row.iloc[k]))

        # 보너스 번호
        bonus = None
        if 'bonus' in df.columns:
            bonus = int(row['bonus'])
        elif '보너스' in df.columns:
            bonus = int(row['보너스'])
        else:
            bonus = int(row.iloc[9])

        # 날짜
        date_val = str(row.iloc[0]) # 첫번째 컬럼이 보통 날짜

        return {
            'numbers': sorted(winning_nums),
            'bonus': bonus,
            'date': date_val
        }
    except Exception as e:
        # print(f"Error parsing winning numbers: {e}")
        return None

def count_matches(recommended_nums, winning_nums):
    return len(set(recommended_nums) & set(winning_nums))

def analyze_recommendations():
    recommendations = parse_recommendation_history()
    results = []
    
    for rec in recommendations:
        target_round = rec['target_round']
        winning_data = get_winning_numbers(target_round)
        
        if not winning_data:
            continue
            
        winning_nums = winning_data['numbers']
        line_results = []
        for i, rec_nums in enumerate(rec['numbers']):
            matches = count_matches(rec_nums, winning_nums)
            line_results.append({
                'line': chr(65 + (i % 5)),
                'set': i // 5 + 1,
                'numbers': rec_nums,
                'matches': matches
            })
        
        max_matches = max(line['matches'] for line in line_results) if line_results else 0
        
        results.append({
            'recommendation_no': rec['recommendation_no'],
            'target_round': target_round,
            'winning_numbers': winning_nums,
            'winning_date': winning_data['date'],
            'line_results': line_results,
            'max_matches': max_matches,
            'total_lines': len(line_results)
        })
    
    return results

def check_latest_round_performance():
    recommendations = parse_recommendation_history()
    if not recommendations: return None
    
    for rec in reversed(recommendations):
        target_round = rec['target_round']
        winning_data = get_winning_numbers(target_round)
        if not winning_data: continue
        
        winning_nums = winning_data['numbers']
        line_results = []
        for i, rec_nums in enumerate(rec['numbers']):
            matches = count_matches(rec_nums, winning_nums)
            set_no = i // 5 + 1
            line_no = chr(65 + (i % 5))
            line_results.append({
                'set': set_no,
                'line': line_no,
                'numbers': rec_nums,
                'matches': matches
            })
        
        max_matches = max(line['matches'] for line in line_results) if line_results else 0
        
        return {
            'recommendation_no': rec['recommendation_no'],
            'target_round': target_round,
            'winning_numbers': winning_nums,
            'winning_date': winning_data['date'],
            'line_results': line_results,
            'max_matches': max_matches
        }
    return None

def get_recommendation_date(recommendation_no):
    result_file = get_file_path('lotto_result.txt')
    if not os.path.exists(result_file): return "날짜 정보 없음"
    
    with open(result_file, encoding='utf-8') as f:
        content = f.read()
    
    pattern = f'{recommendation_no:02d}번째 추천 번호에요~'
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if pattern in line:
            for j in range(max(0, i-10), i):
                date_match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', lines[j])
                if date_match: return date_match.group(1)
            break
    return "날짜 정보 없음"

def generate_performance_report():
    results = analyze_recommendations()
    if not results: return "분석할 추천번호 데이터가 없습니다."
    
    total_recommendations = len(results)
    match_counts = defaultdict(int)
    jackpot_matches = []
    
    for result in results:
        match_counts[result['max_matches']] += 1
        winning_nums = result['winning_numbers']
        for line in result['line_results']:
            if line['matches'] == 6 and set(line['numbers']) == set(winning_nums):
                jackpot_matches.append({
                    'recommendation_no': result['recommendation_no'],
                    'target_round': result['target_round'],
                    'winning_date': result['winning_date'],
                    'line': line,
                    'numbers': line['numbers']
                })
    
    report = []
    report.append("🎯 추천번호 성과 분석 리포트")
    report.append("=" * 30)
    report.append(f"총 추천 횟수: {total_recommendations}회")
    report.append("")
    
    if jackpot_matches:
        report.append("🎊 **1등 당첨번호 발견!**")
        for match in jackpot_matches:
            rec_date = get_recommendation_date(match['recommendation_no'])
            nums_str = ' '.join(map(str, match['numbers']))
            report.append(f"  🏆 {match['recommendation_no']:02d}번째 추천 → {match['target_round']}회차 1등!")
            report.append(f"      번호: {nums_str}")
            report.append(f"      추천생성: {rec_date}")
            report.append(f"      당첨발표: {match['winning_date']}")
    else:
        report.append("📝 **1등 당첨번호 현황**")
        report.append("  아직까지 누적 추천번호 중에 1등 당첨번호는 없었습니다.")
    
    report.append("")
    report.append("📊 최고 적중 개수별 분포:")
    for matches in sorted(match_counts.keys(), reverse=True):
        count = match_counts[matches]
        percentage = (count / total_recommendations) * 100
        report.append(f"  {matches}개 적중: {count}회 ({percentage:.1f}%)")
    
    report.append("")
    report.append("📈 최근 5회 성과:")
    for result in results[-5:]:
        report.append(f"  {result['recommendation_no']:02d}번째 → {result['target_round']}회차: 최대 {result['max_matches']}개 적중")
    
    return "\n".join(report)

if __name__ == "__main__":
    print(generate_performance_report())