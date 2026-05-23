#!/usr/bin/env python3
"""
실제 8단계 (12개 제약) 정확한 곱셈 효과 계산
왜 0개인지 최종 해답
"""

def calculate_real_multiplication_effect():
    """실제 12개 제약 조건의 정확한 곱셈 효과"""
    print("🎯 실제 8단계 (12개 제약) 정확한 곱셈 효과")
    print("=" * 70)
    
    # 실제 제약 조건들과 추정 통과율
    constraints = [
        ("1-1. 구간분배 1~3개", 0.67),      # 67%
        ("1-2. 홀짝균형", 0.97),            # 97%
        ("1-3. 연속번호 3개이하", 0.99),     # 99%
        ("1-4. 끝수중복 3개이하", 0.95),     # 95%
        ("2-1. 합계범위 145~165", 0.23),    # 23% ← 최대 병목!
        ("2-2. 분산범위 80~250", 0.77),     # 77%
        ("2-3. 첫째자리 최대2개", 0.56),     # 56%
        ("2-4. 0,5끝수 최대1개", 0.73),      # 73%
        ("3-1. 빈출번호 최소2개", 0.52),     # 52%
        ("3-2. 저빈출 완전배제", 0.48),     # 48%
        ("4-1. 소수 1~4개", 0.84),          # 84%
        ("4-2. 제곱수 최대1개", 0.87),       # 87%
        ("4-3. 5배수 최대1개", 0.80),        # 80%
        ("4-4. 간격패턴 중복금지", 0.62),    # 62%
        ("5-1. 피보나치 최대2개", 0.78),     # 78%
        ("5-2. 삼각수 최대2개", 0.72),       # 72%
        ("5-3. 연속곱 최대1개", 0.93),       # 93%
        ("5-4. 등차수열 금지", 0.88),        # 88%
        ("5-5. 자릿수합 중복금지", 0.65),    # 65%
        ("5-6. 대칭성 금지", 0.82),          # 82%
        ("6. 패턴유사성 배제", 0.90),        # 90%
        ("7. 중복방지 1,672개", 0.79),       # 79%
        ("8. Top5 특별규칙", 0.85),          # 85%
    ]
    
    print("단계별 누적 통과율:")
    print("-" * 70)
    
    cumulative = 1.0
    stage = 1
    
    for i, (name, rate) in enumerate(constraints):
        cumulative *= rate
        percentage = cumulative * 100
        
        # 단계 구분
        if name.startswith("2-1"):
            stage = 2
        elif name.startswith("3-1"):
            stage = 3
        elif name.startswith("4-1"):
            stage = 4
        elif name.startswith("5-1"):
            stage = 5
        elif name.startswith("6."):
            stage = 6
        elif name.startswith("7."):
            stage = 7
        elif name.startswith("8."):
            stage = 8
        
        if percentage > 0.01:
            print(f"{name}: {rate*100:4.0f}% → 누적 {percentage:8.4f}%")
        else:
            print(f"{name}: {rate*100:4.0f}% → 누적 {percentage:8.6f}%")
    
    final_expected_100k = int(cumulative * 100000)
    final_expected_1m = int(cumulative * 1000000)
    
    print("\n" + "=" * 70)
    print("🎯 최종 결과:")
    print(f"   100,000번 시도 예상 통과: {final_expected_100k}개")
    print(f"   1,000,000번 시도 예상 통과: {final_expected_1m}개")
    print(f"   실제 통과 확률: {cumulative:.8f} ({cumulative*100:.6f}%)")
    
    if final_expected_100k == 0:
        print("\n🚨 결론: 100,000번 시도로는 통과 불가능!")
        print("   → 23개 제약 조건의 곱셈 효과로 확률이 극도로 낮아짐")
        print("   → 이론적으로는 가능하지만 현실적으로는 0개")
        
        # 몇 번 시도해야 1개 나올까?
        if cumulative > 0:
            tries_for_one = int(1 / cumulative)
            print(f"   → 1개 통과하려면 약 {tries_for_one:,}번 시도 필요")
            
            if tries_for_one > 1000000:
                print(f"   → 즉, 백만 번 이상 시도해야 1개 나올 수 있음!")
    
    return cumulative

def find_biggest_bottlenecks():
    """가장 큰 병목 구간들 찾기"""
    print(f"\n" + "=" * 70)
    print("🔍 가장 큰 병목 구간 TOP 5")
    print("=" * 70)
    
    bottlenecks = [
        ("합계범위 145~165", 23.0),
        ("저빈출 완전배제", 48.0),
        ("빈출번호 최소2개", 52.0),
        ("첫째자리 최대2개", 56.0),
        ("간격패턴 중복금지", 62.0),
    ]
    
    print("이 5개 제약이 전체 성공률을 급격히 떨어뜨리는 주범:")
    for i, (name, rate) in enumerate(bottlenecks, 1):
        impact = 100 - rate
        print(f"{i}. {name}: {rate}% 통과 (실패율 {impact}%)")
    
    print(f"\n💡 개선 방안:")
    print("1. 합계범위를 120~190으로 확대")
    print("2. 저빈출 배제를 하위 3개로 완화")
    print("3. 빈출번호를 상위 15개 중 1개로 완화")
    print("4. 첫째자리를 최대 3개로 완화")
    print("5. 간격패턴을 3번 중복까지 허용")

if __name__ == "__main__":
    final_rate = calculate_real_multiplication_effect()
    find_biggest_bottlenecks() 