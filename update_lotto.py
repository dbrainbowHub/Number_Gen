import json
import pandas as pd
import os

# ==========================================
# 경로 자동 인식
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "lotto_latest.json")
CSV_FILE = os.path.join(BASE_DIR, "lotto_total.csv")

def format_korean_date(date_str):
    """
    입력: '2026.01.03'
    출력: '2026년 01월 03일 추첨'
    """
    try:
        if '.' in date_str:
            parts = date_str.split('.')
            if len(parts) == 3:
                return f"{parts[0]}년 {parts[1]}월 {parts[2]}일 추첨"
        return date_str # 변환 실패 시 원본 반환
    except Exception:
        return date_str

def update_csv():
    print(f"DEBUG: Script location: {BASE_DIR}")
    print(f"DEBUG: Looking for JSON at: {JSON_FILE}")

    # 1. JSON 파일 읽기
    if not os.path.exists(JSON_FILE):
        print(f"Error: JSON file not found at {JSON_FILE}")
        return

    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
        # 데이터 구조 파싱 (껍질 벗기기)
        target_data = raw_data
        if isinstance(target_data, list) and len(target_data) > 0:
            target_data = target_data[0]
        if 'lotto_latest' in target_data:
            target_data = target_data['lotto_latest']

        # 데이터 추출
        new_round = int(target_data.get('round') or target_data.get('drwNo'))
        raw_date = target_data.get('date') or target_data.get('drwNoDate') # '2026.01.03'
        
        # [핵심 수정] 사용자가 원하는 한글 포맷으로 변환
        # '2026.01.03' -> '2026년 01월 03일 추첨'
        formatted_date = format_korean_date(raw_date)
        
        if 'numbers' in target_data:
             numbers = target_data['numbers']
        elif 'drwtNo1' in target_data:
             numbers = [target_data[f'drwtNo{i}'] for i in range(1, 7)]
        else:
            print("Error: Cannot find numbers.")
            return

        bonus = int(target_data.get('bonus') or target_data.get('bnusNo'))
        
        print(f"Extracted: {new_round}회 / {formatted_date}")

    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return

    # 2. CSV 파일 읽기 및 업데이트
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            
            # 회차 중복 확인
            if '회차' in df.columns:
                if new_round in df['회차'].values:
                    print(f"Round {new_round} already exists in CSV. Skipping update.")
                    return
            else:
                # 혹시 컬럼명이 다를 경우를 대비 (예: round)
                if 'round' in df.columns and new_round in df['round'].values:
                     print(f"Round {new_round} already exists. Skipping.")
                     return

        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return
    else:
        print("CSV file not found. Creating a new one.")
        # 파일이 없을 때는 헤더를 RB님 파일 형식 그대로 생성
        df = pd.DataFrame(columns=['년도', '회차', '추첨일', '1', '2', '3', '4', '5', '6', '보너스'])

    # 3. 새로운 데이터 행 생성 (형식 완벽 일치)
    # RB님의 요청: "년도"와 "추첨일" 컬럼에 모두 'YYYY년 MM월 DD일 추첨' 형식이 들어감
    new_row_data = {
        '년도': formatted_date,  # 예: 2026년 01월 03일 추첨
        '회차': new_round,       # 예: 1205
        '추첨일': formatted_date, # 예: 2026년 01월 03일 추첨
        '1': numbers[0],
        '2': numbers[1],
        '3': numbers[2],
        '4': numbers[3],
        '5': numbers[4],
        '6': numbers[5],
        '보너스': bonus
    }

    # 데이터프레임 병합
    new_df = pd.DataFrame([new_row_data])
    
    # 컬럼 순서가 중요하므로 기존 df의 컬럼 순서대로 정렬 시도
    if not df.empty:
        new_df = new_df[df.columns]
        
    df = pd.concat([df, new_df], ignore_index=True)

    # 4. 저장 (한글 깨짐 방지 utf-8)
    try:
        df.to_csv(CSV_FILE, index=False, encoding='utf-8')
        print(f"Successfully updated round {new_round} to CSV with format: {formatted_date}")
    except Exception as e:
        print(f"Error saving CSV file: {e}")

if __name__ == "__main__":
    update_csv()