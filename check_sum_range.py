#!/usr/bin/env python3
"""
실제 당첨번호 합계 분포 분석
145~165 범위가 적절한지 검증
"""

import csv
import statistics

def analyze_actual_sum_distribution():
    """실제 당첨번호 합계 분포 분석"""
    print("🎯 실제 당첨번호 합계 분포 분석")
    print("=" * 60)
    
    totals = []
    
    try:
        with open('lotto_total.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # 헤더 스킵
            for row in reader:
                try:
                    nums = [int(n) for n in row[3:9] if n.isdigit()]
                    if len(nums) == 6:
                        totals.append(sum(nums))
                except:
                    continue
    except FileNotFoundError:
        print("❌ lotto_total.csv 파일을 찾을 수 없습니다.")
        return
    
    if not totals:
        print("❌ 데이터를 읽을 수 없습니다.")
        return
    
    # 기본 통계
    mean_val = statistics.mean(totals)
    median_val = statistics.median(totals)
    std_val = statistics.stdev(totals)
    min_val = min(totals)
    max_val = max(totals)
    
    print(f"📊 기본 통계 ({len(totals)}회차)")
    print(f"   평균: {mean_val:.1f}")
    print(f"   중앙값: {median_val:.1f}")
    print(f"   표준편차: {std_val:.1f}")
    print(f"   최소값: {min_val}")
    print(f"   최대값: {max_val}")
    
    # 범위별 분포
    print(f"\n📈 범위별 분포:")
    ranges = [
        (80, 100), (100, 120), (120, 140), (140, 160), 
        (160, 180), (180, 200), (200, 220), (220, 250)
    ]
    
    for start, end in ranges:
        count = sum(1 for t in totals if start <= t < end)
        pct = count/len(totals)*100
        bar = "█" * int(pct/2)  # 시각화
        print(f"   {start:3d}~{end-1:3d}: {count:3d}회 ({pct:5.1f}%) {bar}")
    
    # 145~165 범위 상세 분석
    range_145_165 = sum(1 for t in totals if 145 <= t <= 165)
    pct_145_165 = range_145_165/len(totals)*100
    
    print(f"\n🎯 145~165 범위 분석:")
    print(f"   해당 범위: {range_145_165}회 ({pct_145_165:.1f}%)")
    
    # 다른 범위들과 비교
    other_ranges = [
        ("120~180", 120, 180),
        ("130~170", 130, 170),
        ("135~175", 135, 175),
        ("140~170", 140, 170),
        ("평균±1σ", int(mean_val-std_val), int(mean_val+std_val)),
        ("평균±1.5σ", int(mean_val-1.5*std_val), int(mean_val+1.5*std_val)),
    ]
    
    print(f"\n🔍 다른 범위들과 비교:")
    for name, start, end in other_ranges:
        count = sum(1 for t in totals if start <= t <= end)
        pct = count/len(totals)*100
        print(f"   {name}: {start}~{end} → {count}회 ({pct:.1f}%)")
    
    # 결론
    print(f"\n💡 결론:")
    if pct_145_165 < 30:
        print(f"   ⚠️  145~165 범위는 {pct_145_165:.1f}%로 다소 엄격합니다.")
        
        # 더 적절한 범위 제안
        better_start = int(mean_val - 0.8 * std_val)
        better_end = int(mean_val + 0.8 * std_val)
        better_count = sum(1 for t in totals if better_start <= t <= better_end)
        better_pct = better_count/len(totals)*100
        
        print(f"   💡 추천 범위: {better_start}~{better_end} → {better_pct:.1f}% 커버")
    else:
        print(f"   ✅ 145~165 범위는 {pct_145_165:.1f}%로 적절합니다.")
    
    return totals, pct_145_165

def analyze_recent_vs_all():
    """최근 회차 vs 전체 회차 비교"""
    print(f"\n" + "=" * 60)
    print("🔍 최근 회차 vs 전체 회차 합계 비교")
    print("=" * 60)
    
    all_totals = []
    recent_totals = []
    
    try:
        with open('lotto_total.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # 헤더 스킵
            rows = list(reader)
            
            for row in rows:
                try:
                    nums = [int(n) for n in row[3:9] if n.isdigit()]
                    if len(nums) == 6:
                        total = sum(nums)
                        all_totals.append(total)
                        
                        # 최근 100회차
                        if len(rows) - rows.index(row) <= 100:
                            recent_totals.append(total)
                except:
                    continue
    except:
        return
    
    if len(recent_totals) > 0:
        all_mean = statistics.mean(all_totals)
        recent_mean = statistics.mean(recent_totals)
        
        all_145_165 = sum(1 for t in all_totals if 145 <= t <= 165)
        recent_145_165 = sum(1 for t in recent_totals if 145 <= t <= 165)
        
        all_pct = all_145_165/len(all_totals)*100
        recent_pct = recent_145_165/len(recent_totals)*100
        
        print(f"전체 {len(all_totals)}회차:")
        print(f"   평균: {all_mean:.1f}")
        print(f"   145~165: {all_pct:.1f}%")
        
        print(f"\n최근 {len(recent_totals)}회차:")
        print(f"   평균: {recent_mean:.1f}")
        print(f"   145~165: {recent_pct:.1f}%")
        
        if abs(recent_pct - all_pct) > 5:
            print(f"\n⚠️  최근 트렌드가 전체와 {abs(recent_pct - all_pct):.1f}% 차이납니다.")

if __name__ == "__main__":
    result = analyze_actual_sum_distribution()
    if result:
        totals, pct = result
    analyze_recent_vs_all() 