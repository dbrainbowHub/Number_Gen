import re
import os
from collections import defaultdict
import pandas as pd

def parse_recommendation_history():
    """lotto_result.txt에서 모든 추천번호 기록을 파싱"""
    if not os.path.exists('lotto_result.txt'):
        return []
    
    with open('lotto_result.txt', encoding='utf-8') as f:
        content = f.read()
    
    # 각 추천 블록을 찾기 (하트 이모지 포함 형식)
    blocks = re.split(r'(\d{2})번째 추천 번호에요~[❤️]*', content)
    recommendations = []
    
    # blocks는 [빈내용, 번호, 블록내용, 번호, 블록내용, ...] 형태
    for i in range(1, len(blocks), 2):
        if i + 1 >= len(blocks):
            break
            
        rec_no = int(blocks[i])
        block = blocks[i + 1]
        
        # 회차 정보 추출 (있을 경우)
        round_match = re.search(r'\[직전회차 (\d+)회\]', block)
        if round_match:
            round_no = int(round_match.group(1))
            target_round = round_no + 1
        else:
            # 회차 정보가 없는 경우, 추천번호 순서로 추정
            # 최신 로또 파일에서 최신 회차를 찾아서 계산
            import glob
            lotto_files = glob.glob('lotto_*.csv')
            # 숫자로 된 회차 파일만 필터링
            numeric_files = []
            for f in lotto_files:
                try:
                    # lotto_1234.csv 형태의 파일만 처리
                    round_num = f.split('_')[1].split('.')[0]
                    int(round_num)  # 숫자인지 확인
                    numeric_files.append(f)
                except (ValueError, IndexError):
                    continue  # 숫자가 아니면 건너뛰기
                    
            if numeric_files:
                latest_file = max(numeric_files, key=lambda x: int(x.split('_')[1].split('.')[0]))
                try:
                    df = pd.read_csv(latest_file)
                    latest_round = df['회차'].max()
                    # 추천번호 순서에 따라 대상 회차 추정
                    target_round = latest_round + rec_no - 5  # 대략적인 계산
                except:
                    target_round = 1170 + rec_no  # 기본값
            else:
                target_round = 1170 + rec_no  # 기본값
        
        # A~E 라인별 번호 추출
        numbers = []
        lines = block.split('\n')
        current_set = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # A~E로 시작하는 라인 찾기
            line_match = re.match(r'^([A-E]): ([\d\s]+)', line)
            if line_match:
                nums = [int(x) for x in line_match.group(2).split()]
                if len(nums) == 6:  # 정확히 6개 번호인지 확인
                    current_set.append(nums)
                    
                    # 5개 라인(A~E)이 모이면 하나의 세트 완성
                    if len(current_set) == 5:
                        numbers.extend(current_set)
                        current_set = []
        
        # 마지막 세트 추가
        if current_set:
            numbers.extend(current_set)
        
        if numbers:  # 번호가 추출된 경우에만 추가
            recommendations.append({
                'recommendation_no': rec_no,
                'target_round': target_round,
                'numbers': numbers
            })
    
    return recommendations

def get_winning_numbers(round_no):
    """특정 회차의 당첨번호를 가져오기"""
    try:
        # 최신 lotto 파일 찾기
        import glob
        lotto_files = glob.glob('lotto_*.csv')
        # 숫자로 된 회차 파일만 필터링
        numeric_files = []
        for f in lotto_files:
            try:
                # lotto_1234.csv 형태의 파일만 처리
                round_num = f.split('_')[1].split('.')[0]
                int(round_num)  # 숫자인지 확인
                numeric_files.append(f)
            except (ValueError, IndexError):
                continue  # 숫자가 아니면 건너뛰기
                
        if not numeric_files:
            return None
            
        latest_file = max(numeric_files, key=lambda x: int(x.split('_')[1].split('.')[0]))
        df = pd.read_csv(latest_file)
        
        # 해당 회차 찾기
        round_data = df[df['회차'] == round_no]
        if round_data.empty:
            return None
            
        row = round_data.iloc[0]
        winning_nums = [int(row[str(i)]) for i in range(1, 7)]
        bonus = int(row['보너스']) if '보너스' in row else None
        
        return {
            'numbers': sorted(winning_nums),
            'bonus': bonus,
            'date': row['추첨일']
        }
    except Exception:
        return None

def count_matches(recommended_nums, winning_nums):
    """추천번호와 당첨번호의 일치 개수 계산"""
    return len(set(recommended_nums) & set(winning_nums))

def analyze_recommendations():
    """모든 추천번호의 적중률 분석"""
    recommendations = parse_recommendation_history()
    results = []
    
    for rec in recommendations:
        target_round = rec['target_round']
        winning_data = get_winning_numbers(target_round)
        
        if not winning_data:
            continue
            
        winning_nums = winning_data['numbers']
        
        # 각 라인별 적중 개수 계산
        line_results = []
        for i, rec_nums in enumerate(rec['numbers']):
            matches = count_matches(rec_nums, winning_nums)
            line_results.append({
                'line': chr(65 + (i % 5)),  # A, B, C, D, E
                'set': i // 5 + 1,  # 1, 2, 3세트
                'numbers': rec_nums,
                'matches': matches
            })
        
        # 최고 적중 개수
        max_matches = max(line['matches'] for line in line_results)
        
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
    """최신 회차에 대한 추천번호 성과 확인"""
    recommendations = parse_recommendation_history()
    if not recommendations:
        return None
    
    # 최신 추천번호부터 역순으로 확인하여 분석 가능한 것 찾기
    for rec in reversed(recommendations):
        target_round = rec['target_round']
        
        # 해당 회차 당첨번호 확인
        winning_data = get_winning_numbers(target_round)
        if not winning_data:
            continue  # 당첨번호가 없으면 다음으로
        
        winning_nums = winning_data['numbers']
        
        # 적중률 계산
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
        
        max_matches = max(line['matches'] for line in line_results)
        
        return {
            'recommendation_no': rec['recommendation_no'],
            'target_round': target_round,
            'winning_numbers': winning_nums,
            'winning_date': winning_data['date'],
            'line_results': line_results,
            'max_matches': max_matches
        }
    
    # 분석 가능한 추천번호가 없음
    return None

def generate_performance_report():
    """전체 추천번호 성과 리포트 생성"""
    results = analyze_recommendations()
    if not results:
        return "분석할 추천번호 데이터가 없습니다."
    
    # 통계 계산
    total_recommendations = len(results)
    match_counts = defaultdict(int)
    
    # 1등 일치 확인을 위한 변수
    jackpot_matches = []
    
    for result in results:
        match_counts[result['max_matches']] += 1
        
        # 6개 완전 일치 (1등) 확인
        winning_nums = result['winning_numbers']
        for line in result['line_results']:
            if line['matches'] == 6:
                # 완전 일치하는 경우 확인 (순서 상관없이)
                if set(line['numbers']) == set(winning_nums):
                    jackpot_matches.append({
                        'recommendation_no': result['recommendation_no'],
                        'target_round': result['target_round'],
                        'winning_date': result['winning_date'],
                        'line': line,
                        'numbers': line['numbers']
                    })
    
    # 리포트 생성
    report = []
    report.append("🎯 추천번호 성과 분석 리포트")
    report.append("=" * 30)
    report.append(f"총 추천 횟수: {total_recommendations}회")
    report.append("")
    
    # 1등 당첨번호 일치 여부
    if jackpot_matches:
        report.append("🎊 **1등 당첨번호 발견!**")
        for match in jackpot_matches:
            # 추천번호 생성 날짜 찾기
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
    
    # 적중 개수별 통계
    report.append("📊 최고 적중 개수별 분포:")
    for matches in sorted(match_counts.keys(), reverse=True):
        count = match_counts[matches]
        percentage = (count / total_recommendations) * 100
        report.append(f"  {matches}개 적중: {count}회 ({percentage:.1f}%)")
    
    # 최근 5회 성과
    report.append("")
    report.append("📈 최근 5회 성과:")
    for result in results[-5:]:
        report.append(f"  {result['recommendation_no']:02d}번째 → {result['target_round']}회차: 최대 {result['max_matches']}개 적중")
    
    return "\n".join(report)

def get_recommendation_date(recommendation_no):
    """추천번호 생성 날짜 찾기"""
    if not os.path.exists('lotto_result.txt'):
        return "날짜 정보 없음"
    
    with open('lotto_result.txt', encoding='utf-8') as f:
        content = f.read()
    
    # 해당 추천번호 블록 찾기
    pattern = f'{recommendation_no:02d}번째 추천 번호에요~'
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if pattern in line:
            # 이전 라인들에서 날짜 정보 찾기
            for j in range(max(0, i-10), i):
                # [2025-05-18 10:25:25] 형태의 날짜 찾기
                date_match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', lines[j])
                if date_match:
                    return date_match.group(1)
            break
    
    return "날짜 정보 없음"

if __name__ == "__main__":
    # 테스트 실행
    print(generate_performance_report())
    
    # 최신 회차 성과 확인
    latest = check_latest_round_performance()
    if latest:
        print(f"\n최신 추천번호({latest['recommendation_no']}번째) 성과:")
        print(f"대상 회차: {latest['target_round']}회")
        print(f"당첨번호: {' '.join(map(str, latest['winning_numbers']))}")
        print(f"최대 적중: {latest['max_matches']}개") 