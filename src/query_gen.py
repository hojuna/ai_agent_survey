import json
import os
import pandas as pd
from utils import load_agents, experiment_code


def main():
    if not os.path.exists(f"data/_data/_query/{experiment_code}"):
        os.makedirs(f"data/_data/_query/{experiment_code}")
    """
    1) 에이전트 정보(성별, 나이, 나이대)가 들어있는 result_data를 기반으로,
    2) 각 에이전트마다 (system + user 메시지 + 함수정의) 형태의 요청을 만들어,
    3) JSON Lines(batch) 파일(survey_fc.jsonl)로 생성합니다.
    """

    result_data = load_agents(f"data/_data/_agent/{experiment_code}/agents_{experiment_code}.json")
    

    # 원본 질문 5개
    survey_questions = (
    "1) How would you rate economic conditions in your community today?\n"
    "- Excellent\n"
    "- Good\n"
    "- Only fair\n"
    "- Poor\n\n"
    "2) A year from now, what do you expect economic conditions in your community will be?\n"
    "- Better\n"
    "- Worse\n"
    "- About the same\n\n"
    "3) If more Americans owned guns, do you think there would be...\n"
    "- More crime\n"
    "- Less crime\n"
    "- No difference\n\n"
    "4) Who did you vote for in the 2020 presidential election?\n"
    "- Donald Trump, the Republican\n"
    "- Joe Biden, the Democrat\n"
    "- Jo Jorgensen, the Libertarian candidate\n"
    "- Howie Hawkins, the Green Party candidate\n"
    "- Another candidate\n\n"
    "5) Which statement comes closer to your own view, even if neither is exactly right?\n"
    "- Americans are united when it comes to the most important values\n"
    "- Americans are divided when it comes to the most important values"
    )


    # 함수 호출을 위한 function 정의
    # "surveyFunction" : 파라미터 5개(Q1..Q5)
    functions = [
        {
            "name": "surveyFunction",
            "description": "Provide answers to the survey in a JSON object.",
            "parameters": {
                "type": "object",
                "properties": {
                    "Q1": {"type": "string"},
                    "Q2": {"type": "string"},
                    "Q3": {"type": "string"},
                    "Q4": {"type": "string"},
                    "Q5": {"type": "string"}
                },
                "required": ["Q1", "Q2", "Q3", "Q4", "Q5"]
            }
    }
    ]

    # batch 요청 한 줄 = 하나의 ChatCompletion 요청
    data_list = []
    agent_id = 0
    for agent in result_data:
        agent_id += 1
        gender = agent["gender"]
        age = agent["age"]
        # age_group = agent["age_group"]
        
        system_content = (
            f"You are a survey assistant. The respondent is {gender}, "
            f"age {age}. "
            "Please answer the survey questions in JSON format by calling the function."
        )

        # user 메시지(질문):
        user_content = survey_questions

        # ChatCompletion과 함수 호출 필드 구성
        request_obj = {
            "custom_id": f"request-{agent_id}",  # 고유 ID 생성
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-2024-11-20",
                "messages": [
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ],
                "functions": functions,
                "function_call": {"name": "surveyFunction"},
                "max_tokens": 1000  # 필요에 따라 조정
            }
        }
        
        

        data_list.append(request_obj)

    # survey_fc.jsonl 파일로 저장
    with open(f"data/_data/_query/{experiment_code}/survey_fc_{experiment_code}.jsonl", "w", encoding="utf-8") as f:
        for item in data_list:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Created survey_fc_{experiment_code}.jsonl with {len(data_list)} lines.")

if __name__ == "__main__":
    main()
