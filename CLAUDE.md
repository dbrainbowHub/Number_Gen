# num_gen

## 개요

대한민국 로또6/45 번호 분석 및 추천 디스코드 봇.
전 회차 당첨번호 데이터를 기반으로 통계적·수학적 제약 조건을 적용해 번호를 생성하고,
매주 토요일 23시 자동 스케줄링으로 최신 데이터 업데이트 및 적중 결과를 보고한다.

## 기술 스택

- **언어**: Python 3.7+
- **Discord**: discord.py
- **데이터 처리**: pandas
- **스케줄링**: apscheduler
- **시간대**: pytz
- **환경변수**: python-dotenv

## 빌드 & 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp env_example.txt .env
# .env에 DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID 입력

# 봇 실행
bash start_bot.sh
# 또는
python discord_lotto_bot.py
```

## 테스트

```bash
python test_fix.py
python test_practical.py
```

## 디렉토리 구조

```
num_gen/
├── discord_lotto_bot.py   # 봇 메인 (Discord 이벤트, 명령어, 스케줄러)
├── lotto_generator.py     # 번호 생성 로직 (제약조건 필터링)
├── lotto_analyzer.py      # 분석 기능 (적중 통계, 리포트)
├── update_lotto.py        # CSV 업데이트 (웹 크롤링)
├── merge_lotto.py         # 데이터 병합
├── lotto_total.csv        # 전 회차 당첨번호 원본 데이터
├── lotto_1171.csv~        # 회차별 개별 CSV
├── requirements.txt
├── start_bot.sh / stop_bot.sh
└── .env                   # 시크릿 (gitignore 필수)
```

## 코딩 컨벤션

- 함수 단위 모듈화 (1함수 50줄 이하)
- 환경변수는 반드시 `.env`에서 로드, 하드코딩 금지
- pandas DataFrame은 불변 처리 (inplace=False)
- 예외는 명시적으로 catch 후 로깅
- 파일명: snake_case, 클래스명: PascalCase

## 주요 제약 조건 (번호 생성)

| 항목 | 규칙 |
|------|------|
| 구간 분포 | 1~15, 16~30, 31~45 각 1~3개 |
| 합계 범위 | 145~165 |
| 분산 | 80~250 |
| 홀짝 | 전체 홀수/짝수 조합 제외 |
| 연속 | 4개 이상 연속 금지 |
| 빈출번호 | 상위 12개 중 최소 2개 포함 |
| 중복 방지 | 과거 당첨번호, 추천번호와 완전 중복 배제 |

## 환경변수

```env
DISCORD_BOT_TOKEN=디스코드_봇_토큰
DISCORD_CHANNEL_ID=채널_ID
```

## 작업 규칙 (CRITICAL)

### 수정 전 백업 필수

코드 또는 문서를 수정하기 전에 반드시 원본을 백업한다.

```bash
# 백업 예시
cp lotto_generator.py lotto_generator.py.bak
cp lotto_result.txt lotto_result.txt.bak
```

- 백업 파일명: `원본파일명.bak` 또는 `원본파일명.YYYYMMDD.bak`
- 백업 후 수정 시작, 검증 완료 후 `.bak` 파일 삭제
- `.bak` 파일은 `.gitignore`에 등록되어 있으므로 커밋되지 않음
