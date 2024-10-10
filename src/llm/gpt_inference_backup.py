import os, copy, time
import openai

class GPTPOOL:
    def __init__(self, key_file='keys.txt', model="gpt-3.5-turbo", temp=-1):
        self.key_file = key_file
        self.model = model
        self.temp = temp

    def get_key(self):
        with open(self.key_file, 'r') as f:
            keys = [x.strip() for x in f.readlines()]

        cur_key = copy.deepcopy(keys[0])
        keys = keys[1:]+[cur_key]

        with open(self.key_file, 'w') as f:
            f.write('\n'.join(keys))

        self.cur_key = cur_key

        return cur_key
    
    def query(self, ask, get_lower=False):
        try:
            return self._query(ask, get_lower)
        except Exception as e:
            print(f'Error: {e}')
            if 'maximum context length' in str(e):
                ask = '. '.join(ask.split('. ')[2:])
            time.sleep(2)
            return self.query(ask, get_lower)

    def _query(self, ask, post_process=False, get_lower=False):
        key = self.get_key()
        print(f'cur_key: {key}')
        os.environ["OPENAI_API_KEY"] = key
        openai.api_key = os.getenv("OPENAI_API_KEY")
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=[{
                "role": "system", "content": "Assistant is an intellectual chatbot designed to follow you instructions."
            }, {"role": "user", "content": ask}],
            temperature=self.temp if self.temp != -1 else 1,
        )
        ans = completion.choices[0].message['content']
        if post_process:
            if get_lower:
                ans = ans.lower().strip().replace('\n', ' ').replace('  ', ' ')
            else:
                ans = ans.strip().replace('\n', ' ').replace('  ', ' ')
        return ans