import requests
from utils import get_config

config = get_config("configs/api_config.yml")

def test_opinion(query, seed=3):
    url = f"http://localhost:{config['server']['port']}{config['routes']['opinion_api']}"
    payload = {
        "question": query,
        "seed": seed
    }
    response = requests.post(url, json=payload)
    print("🔍 OpinionBot 回應：")
    print(response.json())

def test_keypo(query):
    url = f"http://localhost:{config['server']['port']}{config['routes']['keypo_api']}"
    payload = {
        "question": query
    }
    response = requests.post(url, json=payload)
    print("🔍 KeypoRAGBot 回應：")
    print(response.json())

if __name__ == "__main__":
    print("=== 機器人測試工具 ===")
    print("請選擇要測試的機器人：")
    print("1. OpinionBot（輿情分析）")
    print("2. KeypoRAGBot（KEYPO 文件問答）")
    
    bot_choice = input("請輸入數字選擇 (輸入 2 才會使用 KeypoRAGBot，其它皆為預設 OpinionBot)：").strip()
    query = input("請輸入你的問題：").strip()

    if bot_choice == "2":
        print("\n✅ 測試 KeypoRAGBot")
        test_keypo(query)
    else:
        seed_input = input("請輸入 seed 值（預設為 3）：").strip()
        seed = int(seed_input) if seed_input else 3
        print("\n✅ 測試 OpinionBot")
        test_opinion(query, seed)