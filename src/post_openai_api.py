from openai import OpenAI
import json
from dotenv import load_dotenv
import os
from utils import experiment_code
load_dotenv()

client = OpenAI()

def main():
    if not os.path.exists(f"data/_data/_batch/{experiment_code}"):
        os.makedirs(f"data/_data/_batch/{experiment_code}")

    batch_input_file = client.files.create(
        file=open(f"data/_data/_query/{experiment_code}/survey_fc_{experiment_code}_test.jsonl", "rb"),
        purpose="batch"
    )

    print(batch_input_file)

    batch_input_file_id = batch_input_file.id
    batch = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "description": "nightly eval job"
        }
    )


    # batch 객체를 dictionary로 변환
    batch_dict = {
        "id": batch.id,
        "status": batch.status,
        "created_at": batch.created_at,
        "expires_at": batch.expires_at,
        "input_file_id": batch.input_file_id,
        "endpoint": batch.endpoint,
        "completion_window": batch.completion_window,
        "metadata": batch.metadata
    }

    # JSON 파일로 저장
    with open(f'data/_data/_batch/{experiment_code}/batch_info_{experiment_code}.json', 'w', encoding='utf-8') as f:
        json.dump(batch_dict, f, indent=4, ensure_ascii=False)

    print(f"배치 정보가 batch_info_{experiment_code}.json 파일로 저장되었습니다.")

if __name__ == "__main__":
    main()
