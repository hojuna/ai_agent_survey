import pandas as pd
import os

# 실험 코드 01
experiment_code = "01"

def load_agents(filename_json:str=f"data/_data/_agent/{experiment_code}/agents_{experiment_code}.json")->list[dict]:
    df = pd.read_json(filename_json, orient='records')
    return df.to_dict(orient='records')

def save_agents(result_data:list[dict],filename_json:str=f"data/_data/_agent/{experiment_code}/agents_{experiment_code}.json"):
    if not os.path.exists(f"data/_data/_agent/{experiment_code}"):
        os.makedirs(f"data/_data/_agent/{experiment_code}")

    df = pd.DataFrame(result_data)
    df.to_json(filename_json, orient='records', index=False)

