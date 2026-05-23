import pandas as pd

# 파일명 설정
file1 = '600(only_number).csv'
file2 = '1171(only_number).csv'
output_file = 'lotto_total.csv'

# 헤더 없이 바로 읽기
df1 = pd.read_csv(file1, header=None)
df2 = pd.read_csv(file2, header=None)

# 컬럼명 지정 (600, 1171 파일 모두 동일 구조)
columns = ['년도', '회차', '추첨일', '1', '2', '3', '4', '5', '6', '보너스']
df1.columns = columns
df2.columns = columns

# 두 데이터 합치기
df = pd.concat([df1, df2], ignore_index=True)

# 회차 기준 중복 제거(최신 데이터 우선)
df = df.drop_duplicates(subset=['회차'], keep='last')

# 회차 오름차순 정렬
df = df.sort_values(by='회차').reset_index(drop=True)

# csv로 저장
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f'통합 완료! → {output_file}')