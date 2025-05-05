import requests

class RiddleGenerator:
    def __init__(self, api, landmarks, styles) -> None:
        self.api = api
        self.model = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api}"
            }
        self.styles = styles
        self.landmarks = landmarks
        self.rawRiddle = {}
        
    def fetchRiddle(self) -> requests.Response:
        for landmark in self.landmarks:
            if landmark not in self.rawRiddle:
                self.rawRiddle[landmark] = {}
            for style in self.styles:
                if style not in self.rawRiddle[landmark]:
                    self.rawRiddle[landmark][style] = {}
                
                template = self._get_template(style, landmark)
                response = requests.post(
                    self.model,
                    headers=self.headers,
                    json={
                        "model": "gpt-4o",
                        "messages": [
                            {"role": "system", "content": "You are a creative riddle generator."},
                            {"role": "user", "content": template}
                            ],
                            "temperature": 1.0
                        }
                )
                if response.status_code == 200:
                    result = response.json()
                    self.rawRiddle[landmark][style] = result
                else:
                    print(f"Failed to generate riddle for {landmark} ({style})")
                    self.rawRiddle[landmark][style] = None  
        return self

    def _get_template(self, style, landmark):
        return f"""
        Create a {style} riddle about {landmark}. Use the following details:
        - History (if available)
        - Architecture and color
        - Significance
        Keep the riddle concise (max 5 lines) and in a {style} tone.
        """

if __name__ == "__main__":
    ### setting api
    api = []
    with open('openaiAPI.text', 'r') as f:
        a = f.readline().strip()
        api.append(a)
    api_key = api[0]

    ### from pre-processed output
    target_landmarks = []
    with open("outputfiles/pre-processed.json", "r") as f:
        import json
        data = json.load(f)
        for name, info in data.items():
            target_landmarks.append(name)
    
    styles = ["medieval"]

    generator = RiddleGenerator(api_key, target_landmarks, ["medieval", "mysterious"])
    
    # trial fetch
    # generator.fetchRiddle()
    # riddles = generator.rawRiddle
    # with open("outputfiles/unprocessed_riddles.json", "w") as file:
    #     import json
    #     json.dump(riddles, file, indent=2)




    ### generating riddle
    # generator = RiddleGenerator(api_key, "Glucksman Gallery")

    # response = generator.fetchRiddle()

    # if response.status_code == 200:
    #     # 打印响应内容
    #     with open("outputfiles/sample_riddle.json", "w") as file:
    #         import json
    #         json.dump(response.json(), file, indent=4)
    #         print("successful generate!")
    # else:
    #     print(f"Request failed with status code {response.status_code}")
        

    