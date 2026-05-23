"""
Obsidian 동기화 스크립트
/Users/db_rainbow/Desktop/TedsStory/HomePage/Num_Gen/ 에 프로젝트 문서를 저장한다.
"""

import os
import re
import csv
import datetime
from collections import Counter
from pathlib import Path

OBSIDIAN_DIR = Path("/Users/db_rainbow/Desktop/TedsStory/HomePage/Num_Gen")
RESULT_FILE  = Path("lotto_result.txt")
TOTAL_CSV    = Path("lotto_total.csv")


# ── 유틸 ────────────────────────────────────────────────────────────────────

def today() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d")

def now_str() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def load_winning(round_no: int):
    """lotto_total.csv에서 특정 회차 당첨번호 반환"""
    if not TOTAL_CSV.exists():
        return None
    with open(TOTAL_CSV, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            try:
                if int(row[1]) == round_no:
                    return [int(row[i]) for i in range(3, 9)]
            except (ValueError, IndexError):
                continue
    return None


# ── 추천번호 이력 파싱 ──────────────────────────────────────────────────────

def parse_recommendations():
    if not RESULT_FILE.exists():
        return []

    content = RESULT_FILE.read_text(encoding="utf-8")
    blocks  = re.split(r'(\d{2})번째 추천 번호에요~[❤️]*', content)
    recs    = []

    for i in range(1, len(blocks), 2):
        if i + 1 >= len(blocks):
            break
        rec_no = int(blocks[i])
        block  = blocks[i + 1]

        round_match = re.search(r'\[직전회차 (\d+)회\]', block)
        prev_round  = int(round_match.group(1)) if round_match else None
        target_round = (prev_round + 1) if prev_round else None

        sets = []
        for line in block.split("\n"):
            m = re.match(r'^([A-E]): ([\d\s]+)', line.strip())
            if m:
                nums = [int(x) for x in m.group(2).split()]
                if len(nums) == 6:
                    sets.append(nums)

        if sets:
            recs.append({
                "no":           rec_no,
                "prev_round":   prev_round,
                "target_round": target_round,
                "sets":         sets,
            })

    return recs


# ── 문서 1: 추천번호 이력 ───────────────────────────────────────────────────

def build_history_note(recs):
    lines = [
        "---",
        "updated: " + now_str(),
        "tags: [num_gen, 추천이력]",
        "---",
        "",
        "# 추천번호 전체 이력",
        "",
        f"> 총 {len(recs)}회 추천 | 마지막 업데이트: {now_str()}",
        "",
    ]

    for rec in reversed(recs):  # 최신순
        target = rec["target_round"]
        winning = load_winning(target) if target else None
        winning_set = set(winning) if winning else set()

        lines.append(f"## {rec['no']:02d}회 추천 (대상: {target}회차)")
        if rec["prev_round"]:
            lines.append(f"- 직전회차: {rec['prev_round']}회")
        if winning:
            lines.append(f"- 당첨번호: `{' '.join(map(str, sorted(winning)))}`")
        lines.append("")

        best_match = 0
        for j, nums in enumerate(rec["sets"]):
            label   = chr(65 + j)  # A~O
            s       = set(nums)
            matches = len(s & winning_set) if winning_set else None
            hit_str = f"  → **{matches}개 일치**" if matches is not None else ""
            if matches and matches > best_match:
                best_match = matches
            lines.append(f"- {label}: `{' '.join(map(str, sorted(nums)))}`{hit_str}")

        if winning and best_match >= 3:
            lines.append(f"\n> ✅ 최고 적중: **{best_match}개 일치**")
        lines.append("")

    return "\n".join(lines)


# ── 문서 2: 적중률 분석 ─────────────────────────────────────────────────────

def build_analysis_note(recs):
    match_dist  = Counter()
    best_dist   = Counter()
    valid_count = 0
    total_sets  = 0

    for rec in recs:
        target = rec["target_round"]
        winning = load_winning(target) if target else None
        if not winning:
            continue
        winning_set = set(winning)
        valid_count += 1

        best = 0
        for nums in rec["sets"]:
            m = len(set(nums) & winning_set)
            match_dist[m] += 1
            total_sets += 1
            if m > best:
                best = m
        best_dist[best] += 1

    lines = [
        "---",
        "updated: " + now_str(),
        "tags: [num_gen, 분석, 적중률]",
        "---",
        "",
        "# 적중률 분석 리포트",
        "",
        f"> 분석 회차: {valid_count}회 | 분석 세트: {total_sets}개 | 업데이트: {now_str()}",
        "",
        "## 세트별 적중 분포 (전체 세트 기준)",
        "",
        "| 일치 수 | 건수 | 비율 |",
        "|---------|------|------|",
    ]
    for k in range(6):
        v   = match_dist[k]
        pct = v / total_sets * 100 if total_sets else 0
        lines.append(f"| {k}개 | {v} | {pct:.1f}% |")

    lines += [
        "",
        "## 회차별 최고 적중 분포",
        "",
        "| 최고 일치 | 회차 수 | 비율 |",
        "|----------|---------|------|",
    ]
    for k in range(6):
        v   = best_dist[k]
        pct = v / valid_count * 100 if valid_count else 0
        lines.append(f"| {k}개 | {v} | {pct:.1f}% |")

    p3 = sum(best_dist[k] for k in range(3, 7))
    p3_pct = p3 / valid_count * 100 if valid_count else 0
    lines += [
        "",
        "## 요약",
        "",
        f"- **3개 이상 적중 회차**: {p3}회 / {valid_count}회 ({p3_pct:.1f}%)",
        f"- **4개 이상 적중 회차**: {best_dist[4] + best_dist[5] + best_dist[6]}회",
        f"- **세트당 평균 적중**: {sum(k*v for k,v in match_dist.items())/total_sets:.2f}개" if total_sets else "",
    ]

    return "\n".join(lines)


# ── 문서 3: 프로젝트 현황 대시보드 ─────────────────────────────────────────

def build_dashboard_note(recs):
    latest = recs[-1] if recs else None
    total_recs = len(recs)

    # 최근 5회 성과
    recent_summary = []
    for rec in recs[-5:]:
        target  = rec["target_round"]
        winning = load_winning(target) if target else None
        if winning:
            winning_set = set(winning)
            best = max(len(set(nums) & winning_set) for nums in rec["sets"])
            recent_summary.append(f"{target}회: 최고 {best}개")

    lines = [
        "---",
        "updated: " + now_str(),
        "tags: [num_gen, 대시보드]",
        "---",
        "",
        "# Num_Gen 프로젝트 대시보드",
        "",
        f"## 현황",
        f"- **총 추천 횟수**: {total_recs}회",
        f"- **최신 대상 회차**: {latest['target_round'] if latest else 'N/A'}회",
        f"- **마지막 업데이트**: {now_str()}",
        f"- **GitHub**: [Number_Gen](https://github.com/dbrainbowHub/Number_Gen)",
        "",
        "## 최근 5회 성과",
        "",
    ]
    for s in reversed(recent_summary):
        lines.append(f"- {s}")

    lines += [
        "",
        "## 빠른 링크",
        "",
        "- [[추천번호_이력]]",
        "- [[적중률_분석]]",
        "- [[Number_Generator]]",
        "- [[(Num_Generator) Discord Bot]]",
    ]

    return "\n".join(lines)


# ── 메인 ────────────────────────────────────────────────────────────────────

def sync():
    OBSIDIAN_DIR.mkdir(parents=True, exist_ok=True)
    recs = parse_recommendations()
    print(f"[INFO] 추천 기록 {len(recs)}건 파싱 완료")

    files = {
        "추천번호_이력.md":  build_history_note(recs),
        "적중률_분석.md":    build_analysis_note(recs),
        "Num_Gen_대시보드.md": build_dashboard_note(recs),
    }

    for filename, content in files.items():
        path = OBSIDIAN_DIR / filename
        path.write_text(content, encoding="utf-8")
        print(f"[OK] {filename} 저장 완료 ({len(content.splitlines())}줄)")

    print(f"\n[DONE] Obsidian 동기화 완료 → {OBSIDIAN_DIR}")


if __name__ == "__main__":
    sync()
