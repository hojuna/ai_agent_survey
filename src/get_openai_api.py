from openai import OpenAI
import json
from dotenv import load_dotenv
import os
import csv
from utils import experiment_code
import pandas as pd
load_dotenv()

client = OpenAI()

def parse_responses(file_response, delimiter="==========")->list[dict]:
    """
    주어진 파일에서 JSON 응답을 파싱하여 custom_id와 설문 답변을 추출합니다.
    
    Parameters:
    - file_path (str): JSON 응답이 포함된 텍스트 파일의 경로.
    - delimiter (str): JSON 객체를 구분하는 구분자 문자열.
    
    Returns:
    - list of dict: 각 응답의 custom_id와 Q1~Q5 답변을 포함하는 리스트.

    
    """
    result = []  # 최종 결과를 담을 단일 리스트
    
    for line in file_response.text.strip().split('\n'):
        json_data = json.loads(line)        
        print("\n===========")
        content = json.dumps(json_data, indent=2, ensure_ascii=False)
    
        # 구분자를 기준으로 JSON 객체 분리
        json_strings = content.split(delimiter)
        
        for json_str in json_strings:
            json_str = json_str.strip()
            if not json_str:
                continue
            
            try:
                response_obj = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"JSON 디코딩 에러: {e}")
                continue
            
            # custom_id 추출
            custom_id = response_obj.get("custom_id", "")
            
            # function_call의 arguments 추출
            try:
                arguments_str = response_obj["response"]["body"]["choices"][0]["message"]["function_call"]["arguments"]
                arguments = json.loads(arguments_str)
            except (KeyError, json.JSONDecodeError) as e:
                print(f"Arguments 추출 에러 (custom_id: {custom_id}): {e}")
                arguments = {}
            
            # 딕셔너리를 바로 result에 추가
            result.append({
                "custom_id": custom_id,
                "Q1": arguments.get("Q1", ""),
                "Q2": arguments.get("Q2", ""),
                "Q3": arguments.get("Q3", ""),
                "Q4": arguments.get("Q4", ""),
                "Q5": arguments.get("Q5", "")
            })
    
    return result  # 단일 리스트 반환

def save_to_csv(data:list[dict], output_file:str):
    """
    파싱된 데이터를 CSV 파일로 저장합니다.
    
    Parameters:
    - data (list of dict): 파싱된 응답 데이터 리스트.
    - output_file (str): 저장할 CSV 파일의 경로.
    """
    fieldnames = ["custom_id", "Q1", "Q2", "Q3", "Q4", "Q5"]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    
    print(f"CSV 파일로 저장 완료: {output_file}")

def save_result_csv(experiment_code:str, batch_id:str):
    # 1. JSON 파일 읽기
    with open(f'data/_data/_agent/{experiment_code}/agents_{experiment_code}.json', 'r', encoding='utf-8') as f:
        agents_data = pd.DataFrame(json.load(f))


    # 2. CSV 파일 읽기
    survey_data = pd.read_csv(f'data/_data/_result/{experiment_code}/batch_{experiment_code}_{batch_id}.csv')
    
    # 3. 응답 매핑 정의
    q1_mapping = {
        'Excellent': 1,
        'Good': 2,
        'Only fair': 3,
        'Poor': 4
    }

    q2_mapping = {
        'Better': 1,
        'Worse': 2,
        'About the same': 3
    }

    q3_mapping = {
        'More crime': 1,
        'Less crime': 2,
        'No difference': 3
    }

    q4_mapping = {
        'Donald Trump, the Republican': 1,
        'Joe Biden, the Democrat': 2,
        'Jo Jorgensen, the Libertarian candidate': 3,
        'Howie Hawkins, the Green Party candidate': 4,
        'Another candidate': 5
    }

    q5_mapping = {
        'Americans are united when it comes to the most important values': 1,
        'Americans are divided when it comes to the most important values': 2
    }

    # 4. 응답을 정수로 변환
    survey_data['Q1'] = survey_data['Q1'].map(q1_mapping)
    survey_data['Q2'] = survey_data['Q2'].map(q2_mapping)
    survey_data['Q3'] = survey_data['Q3'].map(q3_mapping)
    survey_data['Q4'] = survey_data['Q4'].map(q4_mapping)
    survey_data['Q5'] = survey_data['Q5'].map(q5_mapping)

    # 5. 데이터 결합 (컬럼명 수정)
    result_df = pd.merge(
        agents_data[['request_id', 'age', 'age_group', 'gender']], 
        survey_data[['custom_id', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5']], 
        left_on='request_id', 
        right_on='custom_id'
    )

    # 6. 컬럼 이름 변경
    result_df = result_df.rename(columns={
        'request_id': 'id',
        'age_group': 'agecat',
        'Q1': 'ECON1MOD',
        'Q2': 'ECON1BMOD',
        'Q3': 'VOTEGEN_POST',
        'Q4': 'MOREGUNIMPACT',
        'Q5': 'UNITY'
    })

    # 7. 필요한 컬럼만 선택하여 저장
    final_df = result_df[['id', 'age', 'agecat', 'gender', 'ECON1MOD', 'ECON1BMOD', 
                        'VOTEGEN_POST', 'MOREGUNIMPACT', 'UNITY']]

    # 8. CSV 파일로 저장
    final_df.to_csv(f'data/_data/_result/{experiment_code}/survey_results_{experiment_code}.csv', index=False)

    print(final_df)
    print("매핑 결과:")
    print("\nECON1MOD (Q1):", q1_mapping)
    print("\nECON1BMOD (Q2):", q2_mapping)
    print("\nVOTEGEN_POST (Q3):", q3_mapping)
    print("\nMOREGUNIMPACT (Q4):", q4_mapping)
    print("\nUNITY (Q5):", q5_mapping)
    print("\n파일이 'survey_results_mapped.csv'로 저장되었습니다.")


def main():
    if not os.path.exists(f"data/_data/_result/{experiment_code}"):
        os.makedirs(f"data/_data/_result/{experiment_code}")

    with open(f'data/_data/_batch/{experiment_code}/batch_info_{experiment_code}.json', 'r') as f:
        batch_info = json.load(f)

    get_batchid = batch_info['id']

    batch = client.batches.retrieve(get_batchid)

    if batch.status == "completed":
        file_response = client.files.content(batch.output_file_id)
        parsed_data = parse_responses(file_response)
        filename = f"data/_data/_result/{experiment_code}/batch_{experiment_code}_{get_batchid}.csv"
        save_to_csv(parsed_data, filename)
        save_result_csv(experiment_code, get_batchid)
    else:
        print("Batch is not completed yet.")



if __name__ == "__main__":
    main()