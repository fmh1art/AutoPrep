class LabelExtractor:
    
    @staticmethod
    def extract_label_of_EM(ans:str):
        ans = ans.lower()
        if 'yes' in ans and 'no' in ans:
            return int(ans.index('yes') < ans.index('no'))
        if 'yes' in ans:
            return 1
        if 'no' in ans:
            return 0