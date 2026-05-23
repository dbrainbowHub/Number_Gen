# num_gen - 기능 명세

## Feature 1: 번호 생성 로직

### 요구사항
1. 전 회차 당첨번호 CSV를 로드하여 빈출/저빈출 통계를 산출한다
2. 구간(1~15, 16~30, 31~45) 각 1~3개 포함 조건을 적용한다
3. 합계 145~165, 분산 80~250 조건을 만족하는 조합만 통과시킨다
4. 홀짝, 연속, 끝수, 소수, 피보나치, 삼각수 등 수학적 제약을 순차 필터링한다
5. 최근 30회차 당첨번호와 5개 이상 일치하는 조합은 제외한다
6. 과거 당첨번호 및 현재 세트 내 중복 조합을 완전 배제한다
7. 조건을 만족하는 조합 중 무작위로 최종 세트를 반환한다

### 데이터 모델
```python
LottoSet = list[int]          # 6개 번호 [1~45]
WinningHistory = pd.DataFrame # columns: round, n1~n6, bonus
FrequencyMap = dict[int, int] # {번호: 출현횟수}
```

### 비즈니스 로직
- Top12 빈출번호 중 최소 2개 포함 강제
- 하위 5개 저빈출번호 완전 배제
- Top5([1,3,7,12,13])와 직전 회차 교집합 기반 일부 번호 강제 포함
- 최근 3회차와 4개 일치 조합 직접 생성 (3·4등 특화)

---

## Feature 2: Discord 봇 명령어

### 요구사항
1. `!num` — 추천 번호 즉시 생성 후 채널에 출력
2. `!anal` — 추천 번호 적중 통계 리포트 출력
3. `!update` — 최신 회차 당첨번호 데이터 수동 갱신
4. `!status` — 봇 상태 및 다음 스케줄 시간 출력
5. `!help` — 명령어 안내 메시지 출력
6. `!test` — 봇 정상 동작 확인용 ping

### API 명세 (Discord 이벤트)
```
on_message(message):
  "!num"    → generate_numbers() → channel.send(result)
  "!anal"   → analyze_results()  → channel.send(report)
  "!update" → update_data()      → channel.send(status)
  "!status" → get_status()       → channel.send(status)
  "!help"   → channel.send(HELP_TEXT)
  "!test"   → channel.send("정상 동작 중")
```

### 비즈니스 로직
- 명령어는 지정된 채널(DISCORD_CHANNEL_ID)에서만 동작
- 오류 발생 시 사용자에게 친화적 에러 메시지 전달
- 명령어 처리 중 예외는 로그에 기록

---

## Feature 3: 자동 스케줄링

### 요구사항
1. 매주 토요일 23:00 KST에 자동 실행
2. 최신 당첨번호 크롤링 → CSV 업데이트
3. 직전 주 추천 번호와 실제 당첨번호 적중 결과 자동 분석
4. 새 추천 번호 생성 → 채널에 자동 발송

### 비즈니스 로직
- apscheduler CronTrigger 사용 (timezone=KST)
- 크롤링 실패 시 재시도 로직 적용 (최대 3회)
- 스케줄 실행 로그 파일(`lotto_update.log`) 기록

---

## Feature 4: 데이터 관리

### 요구사항
1. 회차별 CSV(lotto_NNNN.csv)를 `lotto_total.csv`로 병합한다
2. 신규 회차 데이터 웹 크롤링 후 CSV 추가
3. 데이터 무결성 검증 (6개 번호, 1~45 범위, 중복 없음)
4. 백업 디렉토리에 이전 버전 보관

### 데이터 모델
```
lotto_total.csv:
  round  | n1 | n2 | n3 | n4 | n5 | n6 | bonus
  -------|----|----|----|----|----|----|---------
  1171   | 3  | 9  | 17 | 28 | 32 | 39 | 41
```

### 비즈니스 로직
- 중복 회차 데이터 자동 제거
- 회차 번호 기준 오름차순 정렬 유지
- 크롤링 소스: 동행복권 공식 API
