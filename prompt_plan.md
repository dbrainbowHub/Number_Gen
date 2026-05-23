# num_gen - 구현 계획

## Phase 1: 데이터 기반 안정화
- [ ] `lotto_total.csv` 무결성 검증 스크립트 작성
- [ ] 회차별 CSV → total 자동 병합 로직 검증 (`merge_lotto.py`)
- [ ] 크롤링 실패 시 재시도(최대 3회) 로직 추가 (`update_lotto.py`)
- [ ] 데이터 백업 자동화 (업데이트 전 backup/ 복사)

## Phase 2: 번호 생성 로직 강화
- [ ] 제약조건 단위 테스트 작성 (`test_fix.py` 확장)
- [ ] 생성 실패율 측정 및 로깅 추가
- [ ] 3·4등 특화 로직 검증 (최근 3회차 4개 일치)
- [ ] 생성 성능 프로파일링 (목표: 1세트 < 1초)

## Phase 3: Discord 봇 안정화
- [ ] 명령어별 에러 핸들링 강화
- [ ] 지정 채널 외 명령어 무시 로직 검증
- [ ] `!anal` 리포트 포맷 개선 (적중 분포 시각화)
- [ ] 봇 재시작 시 스케줄 복구 확인

## Phase 4: 자동 스케줄링 검증
- [ ] KST 시간대 스케줄러 동작 확인
- [ ] 토요일 23시 자동 실행 dry-run 테스트
- [ ] 스케줄 로그(`lotto_update.log`) 로테이션 설정
- [ ] 크롤링 → 분석 → 발송 전체 파이프라인 E2E 테스트

## Phase 5: 운영 환경 정비
- [ ] `.gitignore` 작성 (`.env`, `*.log`, `__pycache__` 등)
- [ ] `env_example.txt` → `.env.example` 이름 통일
- [ ] `start_bot.sh` / `stop_bot.sh` nohup 안정성 확인
- [ ] GitHub Actions 또는 cron 기반 CI 구성 검토

## 의존성

- Phase 2는 Phase 1(데이터 안정화) 완료 후 진행
- Phase 3은 Phase 2(번호 생성 안정화) 완료 후 진행
- Phase 4, 5는 Phase 3 완료 후 병렬 진행 가능
