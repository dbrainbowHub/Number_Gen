#!/bin/bash
# 옵깃백 — Obsidian 동기화 + GitHub 백업
# 사용법: bash obsidian_git_backup.sh ["커밋 메시지"]

set -e
cd "$(dirname "$0")"

COMMIT_MSG="${1:-옵깃백: $(date '+%Y-%m-%d %H:%M') 자동 백업}"

echo "======================================"
echo " 옵깃백 시작"
echo "======================================"

# 1. Obsidian 동기화
echo ""
echo "[1/3] Obsidian 노트 생성/갱신 중..."
python3 obsidian_sync.py

# 2. Git 스테이징 & 커밋
echo ""
echo "[2/3] GitHub 커밋 준비 중..."
git add -A
git status --short

if git diff --cached --quiet; then
    echo "[INFO] 변경사항 없음 — 커밋 생략"
else
    git commit -m "$COMMIT_MSG"
    echo "[OK] 커밋 완료"
fi

# 3. Push
echo ""
echo "[3/3] GitHub 푸시 중..."
git push origin main
echo "[OK] 푸시 완료"

echo ""
echo "======================================"
echo " 옵깃백 완료"
echo " GitHub : https://github.com/dbrainbowHub/Number_Gen"
echo " Obsidian: ~/Desktop/TedsStory/HomePage/Num_Gen/"
echo "======================================"
