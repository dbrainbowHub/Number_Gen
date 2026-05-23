import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging
import glob
import os
import re

# --------------------------------------------------------------------------
# 설정
# --------------------------------------------------------------------------
# [수정] 검색어를 '로또' -> '로또 당첨번호'로 구체화 (화면 구조가 더 일정함)
LOTTO_URL = 'https://search.daum.net/search?w=tot&q=로또+당첨번호'
TOTAL_FILE = 'lotto_total.csv'
LOG_FILE = 'lotto_update.log'

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# --------------------------------------------------------------------------
# 1. Daum에서 최신 로또 정보 가져오기 (강화된 버전)
# --------------------------------------------------------------------------
def get_latest_lotto():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(LOTTO_URL, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. 회차 찾기 (다중 안전장치)
        text_content = soup.text
        round_no = None
        
        # 방법 A: "0000회 당첨결과" 패턴 찾기 (공백 포함 허용)
        round_match = re.search(r'(\d+)\s*회\s*당첨결과', text_content)
        if round_match:
            round_no = int(round_match.group(1))
        
        # 방법 B: 못 찾았으면, 제목 영역(.f_tit 등)에서 숫자만 추출
        if round_no is None:
            # 다음 검색의 로또 박스 안에서 '회' 자 앞의 숫자 찾기
            titles = soup.select('.lottery_num, .f_tit, .tit_info')
            for t in titles:
                sub_match = re.search(r'(\d+)회', t.text)
                if sub_match:
                    round_no = int(sub_match.group(1))
                    break

        if round_no is None:
            raise Exception("회차 번호를 화면에서 찾을 수 없습니다.")

        # 2. 날짜 찾기 (예: "2026.01.03") -> "2026년 01월 03일 추첨"
        date_str = "날짜미상"
        date_match = re.search(r'(\d{4})\.(\d{2})\.(\d{2})', text_content)
        if date_match:
            y, m, d = date_match.groups()
            date_str = f"{y}년 {m}월 {d}일 추첨"

        # 3. 당첨 번호 찾기
        ball_box = soup.select('.lottery_num .ball')
        if len(ball_box) < 7:
            ball_box = soup.select('span.ball')
            
        extracted_nums = []
        for ball in ball_box:
            if ball.text.strip().isdigit():
                extracted_nums.append(int(ball.text.strip()))

        if len(extracted_nums) < 7:
            raise Exception(f"번호를 7개 찾지 못했습니다. (찾은 개수: {len(extracted_nums)})")

        nums = extracted_nums[:6]
        bonus = extracted_nums[-1]

        # 4. 결과 반환 (기존 구조 유지)
        return {
            "년도": date_str,
            "회차": round_no,
            "추첨일": date_str,
            "1": nums[0],
            "2": nums[1],
            "3": nums[2],
            "4": nums[3],
            "5": nums[4],
            "6": nums[5],
            "보너스": bonus
        }

    except Exception as e:
        logging.error(f"크롤링 에러: {e}")
        raise e

# --------------------------------------------------------------------------
# 2. 파일 관리 (자동 감지)
# --------------------------------------------------------------------------
def get_latest_lotto_file():
    lotto_files = glob.glob('lotto_*.csv')
    if not lotto_files:
        return None
    def extract_round(filename):
        try:
            base = os.path.basename(filename)
            name_part = os.path.splitext(base)[0] # lotto_1205
            return int(name_part.split('_')[1])
        except Exception:
            return 0
    latest_file = max(lotto_files, key=extract_round)
    return latest_file

# --------------------------------------------------------------------------
# 3. 메인 로직 (업데이트)
# --------------------------------------------------------------------------
def update_lotto_csv():
    try:
        # 최신 파일 로드
        latest_file = get_latest_lotto_file()
        if latest_file:
            print(f"[정보] 최신 파일 '{latest_file}'을 로드합니다.")
            df = pd.read_csv(latest_file)
        else:
            print("[정보] 기존 파일이 없어 새로 시작합니다.")
            df = pd.DataFrame()

        # 웹에서 최신 정보 가져오기
        latest = get_latest_lotto()
        
        # 중복 체크
        if not df.empty and latest["회차"] in df["회차"].values:
            print(f"[알림] {latest['회차']}회({latest['추첨일']}) 데이터는 이미 최신입니다.")
            return

        # 새 데이터 추가 및 저장
        df = pd.concat([df, pd.DataFrame([latest])], ignore_index=True)
        
        new_filename = f"lotto_{latest['회차']}.csv"
        df.to_csv(new_filename, index=False, encoding="utf-8-sig")
        
        print(f"\n[성공] {latest['회차']}회 업데이트 완료! -> {new_filename}")
        print(f"결과: {latest['1']} {latest['2']} {latest['3']} {latest['4']} {latest['5']} {latest['6']} + {latest['보너스']}")

    except Exception as e:
        print(f"업데이트 중 오류 발생: {e}")

if __name__ == "__main__":
    update_lotto_csv()