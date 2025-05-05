
class RiddleGenerator:
    def __init__(self, api) -> None:
        self.api = api

if __name__ == "__main__":
    import requests

    api = []
    with open('openaiAPI.text', 'r') as f:
        a = f.readline().strip()
        api.append(a)

    print(api[0])

    import requests
    api_key = api[0]
    style = "medieval"
    name = "Glucksman Gallery"
    content = f"""
    Create a {style} riddle about {name}. Use the following details:
    - History (if available)
    - Architecture and color
    - Significance
    Keep the riddle concise (max 5 lines) and in a {style} tone.
    """


    # 设置请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # 设置请求数据
    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a creative riddle generator."},
            {"role": "user", "content": content}
        ],
        "temperature": 1.0
    }


    # 发送 POST 请求
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)

    # 检查响应状态码
    if response.status_code == 200:
        # 打印响应内容
        with open("sample_riddle.json", "w") as file:
            import json
            json.dump(response.json(), file, indent=4)
    else:
        print(f"Request failed with status code {response.status_code}")
        

    