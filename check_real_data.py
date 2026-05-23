import csv
from collections import Counter

# 실제 빈출번호 확인
frequent_nums = []
with open('lotto_total.csv', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        nums = row[3:9]
        if all(n.isdigit() for n in nums):
            frequent_nums.extend([int(n) for n in nums])

counter = Counter(frequent_nums)
top12_real = [num for num, count in counter.most_common(12)]
bottom5_real = [num for num, count in counter.most_common()[-5:]]

print('=== 실제 데이터 ===')
print('실제 상위12개:', top12_real)
print('실제 하위5개:', bottom5_real)

# 근사치와 비교
approx_top12 = [34, 12, 13, 18, 27, 45, 33, 14, 40, 37, 7, 38]
approx_bottom5 = [26, 30, 36, 41, 42]

print('\n=== 근사치 데이터 ===')
print('근사 상위12개:', approx_top12)
print('근사 하위5개:', approx_bottom5)

print('\n=== 차이 분석 ===')
top12_match = set(top12_real) & set(approx_top12)
bottom5_match = set(bottom5_real) & set(approx_bottom5)

print('상위12개 일치 개수:', len(top12_match))
print('상위12개 일치 번호:', sorted(top12_match))
print('하위5개 일치 개수:', len(bottom5_match))
print('하위5개 일치 번호:', sorted(bottom5_match))

print('\n=== 실제 상위 20개 빈출번호와 출현 횟수 ===')
for i, (num, count) in enumerate(counter.most_common(20)):
    print(f"{i+1:2d}. {num:2d}번: {count}회") 