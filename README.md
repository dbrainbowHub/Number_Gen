# Lotto 6/45 Discord Bot: Analysis & Recommendation (Korea)

This repository provides a Discord bot for analyzing and recommending numbers for the Korean Lotto 6/45 (Donghaeng Lottery).

> **Disclaimer:**
> - The probability of winning the Korean Lotto is 1 in 8,145,060 (~0.0000123%), so statistical analysis does not guarantee any real advantage.
> - Many people want to avoid picking numbers manually or just want to have fun with analysis, so this bot was created with AI and the following logic.
> - This code is for entertainment purposes only and does not guarantee any winnings.

If you have an interesting logic, feel free to contribute!

## Recommendation Logic

This system recommends numbers based on all past winning data of the Korean Lotto 6/45, using various statistical and mathematical constraints, duplication prevention, frequent number utilization, partial match combinations, etc., as actually implemented in the code.

[Main Steps & Actual Constraints]

1. Basic Structure
   - 1~3 numbers from each range (1~15, 16~30, 31~45)
   - Exclude combinations that are all odd or all even
   - No 4 or more consecutive numbers (up to 3 allowed)
   - No more than 3 numbers with the same last digit

2. Statistical Limits
   - Sum: 145~165
   - Variance: 80~250
   - No more than 3 numbers in the same tens digit (10, 20, 30, 40)
   - At most one number ending with 0 or 5

3. Frequent/Infrequent Number Utilization
   - At least 2 from the top 12 most frequent numbers
   - Completely exclude the bottom 5 least frequent numbers
   - 50% chance to prioritize 3~5 from the top 20 frequent numbers

4. Mathematical Patterns
   - 1~4 primes
   - At most 1 square number
   - At most 1 multiple of 5
   - No repeated gaps (differences) more than once

5. Advanced Mathematical Logic
   - At most 2 Fibonacci numbers
   - At most 2 triangular numbers
   - At most 1 consecutive product
   - No 4 or more in arithmetic sequence (same difference)
   - No more than 3 numbers with the same digit sum
   - No more than 1 symmetric pair (e.g., 1↔45, 2↔44)

6. Recent Winning Pattern Similarity Exclusion
   - No 5 or more matches with the last 30 draws
   - No 3 or more identical gap patterns with the last 30 draws

7. Duplication Prevention
   - Completely exclude all past winning numbers, recommended numbers, and duplicates within the current set

8. Top5 Special Rule & 3rd/4th Prize Optimization
   - Force include intersection with Top5 frequent numbers ([1,3,7,12,13]) and the previous draw
   - Directly generate combinations matching 4 numbers with the last 3 draws
   - Clustering based on frequent numbers (common numbers across multiple sets)

---

This logic is implemented 1:1 in the actual code and applies to all recommendation processes.

## Number Recommendation Logic
- **Based on past winning data**
  - Uses the accumulated real Lotto winning data in `lotto_total(-1177).csv`, which is updated weekly with the latest numbers.
- **Basic Filtering**
  - Excludes combinations identical to recent winning numbers
  - Penalizes or excludes abnormal patterns such as consecutive numbers, same last digits, or concentration in specific ranges
- **Statistical Distribution**
  - Combines numbers to match real winning statistics such as odd/even ratio, range distribution, and sum range
- **Randomness Guarantee**
  - Randomly recommends from among combinations that meet the above conditions
- **Analysis Function**
  - Provides a report on how similar the recommended numbers are to past winning patterns and their statistical characteristics

This bot is for fun and reference only and does not guarantee actual winnings.

---

## Main Features
- **Automatic Scheduling Analysis & Recommendation**
  - Every Saturday at 23:00, when the latest Lotto winning numbers are released, the bot automatically:
    - Collects and updates the latest winning numbers
    - Analyzes and reports the match (hit result) between the recommended numbers and the actual winning numbers for the past week
    - Extracts and announces new recommended numbers in the channel
- **Manual Command Support**
  - Users can execute functions at any time by entering the following commands in Discord chat:
    - `!num` : Instantly generate and announce recommended numbers
    - `!anal` : Analyze and report the performance (hit results) and statistics of recommended numbers
    - `!update` : Manually update the latest winning number data
    - `!status` : Check bot status and next schedule
    - `!help` : Show command guide
    - `!test` : Test bot operation
- **Recommendation Number Statistical Analysis**
  - Provides a report on how many numbers matched the actual winning numbers (hit count statistics), notifies when a 1st prize number is found, summarizes the last 5 recommendations, and shows the distribution of hit counts (e.g., 3 matches, 4 matches, etc.)
  - Odd/even, range, sum, etc. are used internally for filtering during recommendation generation, and the analysis report focuses on hit counts
- **Based on Real Winning Data**
  - All recommendations/analyses are based on the actual Lotto winning data for all rounds, such as `lotto_total(-1177).csv`
  - The hit status of recommended numbers, 1st prize discovery, and recent performance are all calculated by comparison with real winning numbers
- **Extensibility**
  - The code is modularized with functions and classes, making it easy to add new analysis logic, filters, or commands

---

## Main Files
- `discord_lotto_bot.py`: Discord bot main file
- `lotto_generator.py`: Lotto number generation logic
- `lotto_analyzer.py`: Lotto analysis functions
- `lotto_total.csv`: Lotto data file
- `start_bot.sh`: Shell script to run the bot
- `.env.example`: Example environment variable file
- `requirements.txt`: Required Python packages

## Installation
1. Clone or download the repository
2. Install Python 3.x
3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and enter your Discord bot token and channel ID
   ```env
   DISCORD_BOT_TOKEN=your_discord_bot_token_here
   DISCORD_CHANNEL_ID=your_channel_id_here
   ```
5. Run the bot
   ```bash
   bash start_bot.sh
   # or
   python discord_lotto_bot.py
   ```

## Notes
- **Never upload your `.env` file to GitHub.**
- **Keep your bot token private.**

## License
MIT License

---

# 대한민국 로또6/45 분석 및 추천 디스코드 봇

이 저장소는 **대한민국의 동행복권 로또6/45**의 당첨번호 분석 및 추천 기능을 제공하는 디스코드 봇입니다.

> **대한민국 로또의 당첨 확률은 무작위 1/8,145,060(약 0.0000123%)로, 실제로 당첨번호 분석은 통계적으로 의미가 없습니다.**
> 하지만 많은 사람들이 수동으로 번호를 정하기 어렵거나 재미로 분석을 원하기에 AI와 함께 만들었으며, 본 봇은 아래와 같은 논리로 번호를 추천합니다.
(순수하게 재미로 만든 코드이며 실제 당첨 보장과는 무관합니다.)

흥미로운 논리가 있다면 추가해 주세요~~

## 번호 추천 논리

이 시스템은 대한민국 로또6/45의 전 회차 당첨번호 데이터를 기반으로,
다양한 통계적·수학적 제약 조건과 중복 방지, 빈출번호 활용, 부분 일치 조합 등
실제 코드에 구현된 로직에 따라 번호를 추천합니다.

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

---

이 논리는 실제 코드와 1:1로 일치하며, 추천번호 생성의 모든 과정에 적용됩니다.

## 번호 추출 논리
- **과거 당첨번호 데이터 기반**
  - `lotto_total(-1177).csv` 파일에 누적된 실제 로또 당첨번호 데이터를 활용하며 최신 번호가 반영된 데이터는 매주 자동 업데이트 됩니다.
- **기본 필터링**
  - 최근 당첨된 번호와 동일한 조합은 제외
  - 연속된 숫자, 동일 끝수, 특정 구간 집중 등 비정상적 패턴은 가중치 부여 또는 제외
- **통계적 분포 반영**
  - 홀짝 비율, 구간별 분포, 합계 범위 등 실제 당첨 통계와 유사하게 번호를 조합
- **랜덤성 보장**
  - 위 조건을 만족하는 여러 조합 중 무작위로 최종 번호를 추천
- **분석 기능**
  - 추천된 번호가 과거 당첨 패턴과 얼마나 유사한지, 통계적으로 어떤 특성을 가지는지 리포트 제공

이 봇은 재미와 참고용으로만 사용하시고, 실제 당첨을 보장하지 않습니다.

---

## 주요 기능
- **자동 스케줄링 분석 및 추천**
  - 매주 토요일에 최신 로또 당첨번호가 공개되면, 23시에 봇이 자동으로 다음 작업을 수행합니다:
    - 최신 당첨번호를 수집하여 데이터에 반영
    - 최근 한 주간 추천된 번호와 실제 당첨번호의 일치 여부(적중 결과) 자동 분석 및 리포트
    - 새로운 추천 번호를 추출하여 채널에 자동으로 안내
- **수동 명령어 지원**
  - 사용자가 디스코드 채팅에서 아래 명령어를 입력하면, 언제든지 기능을 수동으로 실행할 수 있습니다:
    - `!num` : 추천 번호 즉시 생성 및 안내
    - `!anal` : 추천 번호의 성과(적중 결과) 및 통계 분석 리포트 안내
    - `!update` : 최신 당첨번호 데이터 수동 갱신
    - `!status` : 봇 상태 및 다음 스케줄 확인
    - `!help` : 명령어 안내
    - `!test` : 봇 정상 동작 테스트
- **추천 번호 통계 분석**
  - 추천 번호가 실제 당첨번호와 얼마나 일치했는지(적중 개수별 통계), 1등 당첨번호 발견 시 별도 안내, 최근 5회 추천 결과 요약, 전체 추천 중 적중 개수별 분포(예: 3개 일치, 4개 일치 등)를 리포트로 제공합니다.
  - 홀짝, 구간, 합계 등은 추천 생성 시 내부적으로 필터링에 사용되며, 통계 분석 리포트에는 적중 개수 중심의 결과가 제공됩니다.
- **실제 당첨번호 데이터 기반 분석**
  - 모든 추천/분석은 `lotto_total(-1177).csv` 등 실제 로또 당첨번호 전 회차의 데이터를 기반으로 이루어집니다.
  - 추천 번호의 적중 여부, 1등 당첨 발견, 최근 추천의 성과 등은 실제 당첨번호와의 비교를 통해 산출됩니다.
- **확장성**
  - 코드가 함수와 클래스로 모듈화되어 있어, 새로운 분석 로직, 필터, 명령어 등을 추가하기 쉽도록 설계되어 있습니다.

---

## 주요 파일
- `discord_lotto_bot.py`: 디스코드 봇 메인 실행 파일
- `lotto_generator.py`: 로또 번호 생성 로직
- `lotto_analyzer.py`: 로또 분석 기능
- `lotto_total.csv`: 로또 데이터 파일
- `start_bot.sh`: 봇 실행용 셸 스크립트
- `.env.example`: 환경변수 예시 파일
- `requirements.txt`: 필수 파이썬 패키지 목록

## 설치 방법
1. 저장소 클론 또는 파일 다운로드
2. Python 3.x 설치
3. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```
4. `.env.example` 파일을 복사해 `.env`로 만들고, 본인 디스코드 봇 토큰과 채널 ID 입력
   ```env
   DISCORD_BOT_TOKEN=여기에_디스코드_봇_토큰_입력
   DISCORD_CHANNEL_ID=여기에_채널_ID_입력
   ```
5. 봇 실행
   ```bash
   bash start_bot.sh
   # 또는
   python discord_lotto_bot.py
   ```

## 주의사항
- `.env` 파일은 절대 깃허브에 올리지 마세요.
- 봇 토큰은 외부에 노출되지 않도록 주의하세요.

## 라이선스
MIT License 