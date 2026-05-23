import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging
import glob
import os

LOTTO_URL = 'https://dhlottery.co.kr/gameResult.do?method=byWin'
TOTAL_FILE = 'lotto_total.csv'
LOG_FILE = 'lotto_update.log'

# 로깅 설정 (윈도우/리눅스 모두 호환)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def get_latest_lotto():
    try:
        response = requests.get(LOTTO_URL, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        all_div = soup.find("div", {"class": "win_result"})
        tit = all_div.find("h4").get_text().strip()
        round_no = int(''.join(filter(str.isdigit, tit)))
        dtm = all_div.find("p", {"class": "desc"}).text.replace('(', '').replace(')', '').strip()
        div_num_win = soup.find("div", {"class": "num win"})
        balls = div_num_win.find_all("span")
        nums = [int(b.get_text().strip()) for b in balls[:6]]
        div_num_bonus = soup.find("div", {"class": "num bonus"})
        num_bonus = int(div_num_bonus.find_all("span")[0].get_text().strip())
        year = dtm.split('.')[0]
        return {
            "년도": year,
            "회차": round_no,
            "추첨일": dtm,
            "1": nums[0],
            "2": nums[1],
            "3": nums[2],
            "4": nums[3],
            "5": nums[4],
            "6": nums[5],
            "보너스": num_bonus
        }
    except Exception as e:
        logging.error(f"로또 데이터 크롤링 실패: {e}")
        raise

def get_latest_lotto_file():
    lotto_files = glob.glob('lotto_*.csv')
    if not lotto_files:
        return None
    # 파일명에서 회차 추출 후 가장 큰 회차 찾기
    def extract_round(filename):
        try:
            return int(os.path.splitext(os.path.basename(filename))[0].split('_')[1])
        except Exception:
            return 0
    latest_file = max(lotto_files, key=extract_round)
    return latest_file

def update_lotto_csv():
    try:
        # 가장 최근 lotto_*.csv 파일 찾기, 없으면 lotto_total.csv 사용
        latest_file = get_latest_lotto_file()
        if latest_file:
            df = pd.read_csv(latest_file)
        else:
            df = pd.read_csv(TOTAL_FILE)

        latest = get_latest_lotto()
        if latest["회차"] in df["회차"].values:
            logging.info(f"{latest['회차']}회는 이미 데이터에 있습니다.")
            print(f"{latest['회차']}회는 이미 데이터에 있습니다.")
            return

        df = pd.concat([df, pd.DataFrame([latest])], ignore_index=True)
        df = df.sort_values(by="회차").reset_index(drop=True)

        new_filename = f"lotto_{latest['회차']}.csv"
        df.to_csv(new_filename, index=False, encoding="utf-8-sig")
        logging.info(f"{latest['회차']}회 데이터 추가 및 저장 완료 → {new_filename}")
        print(f"{latest['회차']}회 데이터 추가 및 저장 완료 → {new_filename}")
    except Exception as e:
        logging.error(f"업데이트 중 오류 발생: {e}")
        print(f"업데이트 중 오류 발생: {e}")

if __name__ == "__main__":
    update_lotto_csv()
    logging.info("로또 데이터 수동/자동 최신화 1회 실행 완료!")
