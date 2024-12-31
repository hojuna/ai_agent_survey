import random
import statistics
import math

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from utils import experiment_code, save_agents

def truncated_normal_sample(n:int, mean:float, std:float, low:int, high:int)->list[int]:
    """
    [low, high] 구간 내에서 정규분포(gauss) 난수를 생성하되,
    범위를 벗어나면 재샘플링.
    이번 버전은 최종적으로 정수(rounded) 값만 반환.
    """
    samples = []
    for _ in range(n):
        while True:
            val = random.gauss(mean, std)  # 실수
            # 정수로 반올림
            val_rounded = int(round(val))
            if low <= val_rounded <= high:
                samples.append(val_rounded)
                break
    return samples

def generate_ages_for_category(category_id:int, n:int=100)->list[int]:
    """
    category_id에 따라 나이 범위, 목표평균(mean), 표준편차(std)를 설정하고,
    n개의 정수 나이를 샘플링하여 리스트로 반환한다.
    """
    target_means = {
        1: 23.723108,
        2: 39.325035,
        3: 57.406375,
        4: 74.109596
    }
    age_ranges = {
        1: (18, 29),
        2: (30, 49),
        3: (50, 64),
        4: (65, 99)
    }
    
    low, high = age_ranges[category_id]
    range_span = high - low
    std = range_span / 6.0  # 범위 폭에 적당한 표준편차 추정
    mean = target_means[category_id]
    
    # 트런케이트된 정규분포에서 integer 샘플링
    samples = truncated_normal_sample(n, mean, std, low, high)
    
    # 실제 샘플 평균을 확인(오차 감안)
    actual_mean = statistics.mean(samples)

    return samples


def main():
    random.seed(42)  # 재현성을 위해 시드 고정
    genders = ["Male", "Female"]
    categories = [1, 2, 3, 4]
    n_per_combination = 100
    
    result_data = []

    id=0
    
    for cat_id in categories:
        for gender in genders:
            # 해당 (cat_id, gender) 조합에 대해 100개 정수 나이 샘플 생성
            ages = generate_ages_for_category(cat_id, n_per_combination)
            
            for age in ages:
                id+=1
                item = {
                    "request_id": f"request-{id}",
                    "gender": gender,
                    "age_group": cat_id,  
                    "age": age  # 이미 정수
                }
                result_data.append(item)

    
    # 총 8가지 조합 x 각 100개 = 800개
    print(f"Total items: {len(result_data)}")


    plt.style.use('seaborn-v0_8')

    # 데이터를 DataFrame으로 변환
    df = pd.DataFrame(result_data)

    # 그림 크기 설정
    plt.figure(figsize=(15, 8))

    # 나이 그룹별 분포도 그리기
    sns.boxplot(x='age_group', y='age', data=df, hue='gender')
    plt.title('Age Distribution by Age Group and Gender')
    plt.xlabel('Age Group')
    plt.ylabel('Age')
    plt.savefig(f'data/_data/_agent/{experiment_code}/age_distribution_{experiment_code}.png')

    # Histogram of age distribution by group
    g = sns.FacetGrid(df, col='age_group', hue='gender', col_wrap=2, height=4, aspect=1.5)
    g.map(sns.histplot, 'age', bins=20)
    g.fig.suptitle('Age Distribution Histogram by Age Group', y=1.05)
    plt.savefig(f'data/_data/_agent/{experiment_code}/age_distribution_histogram_{experiment_code}.png')

    # Print basic statistics
    print("\n=== Basic Statistics by Age Group ===")
    print(df.groupby('age_group')['age'].describe())

    print("\n=== Mean Age by Gender and Age Group ===")
    print(df.groupby(['age_group', 'gender'])['age'].mean().unstack())

    save_agents(result_data)

if __name__ == "__main__":
    main()