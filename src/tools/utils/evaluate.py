import re
from typing import List

from .standardize import standardize_val, clean_str
from .parse_output import parse_any_string

def wikit_if_hit(pred, label):
    pred = pred.lower()
    label = label.lower()
    if '|' in label:
        labs = [standardize_val(clean_str(x)) for x in label.split('|')]
        preds = [standardize_val(clean_str(x)) for x in pred.split('|')]
        all_match = True
        for l in labs:
            if l not in preds:
                all_match = False
                break
        if all_match:
            return True
    else:
        # if standardize_val(clean_str(label)) == standardize_val(clean_str(pred)):
        if standardize_val(clean_str(label)) == standardize_val(clean_str(pred)) or \
            standardize_val(clean_str(label)) in standardize_val(clean_str(pred)):
            return True
    return False

def tablefact_if_hit(pred, label):
    pred = str(pred).lower()
    label = str(label).lower()
    pred = parse_any_string(pred)
    if label == '1':
        return pred == 'true'
    else:
        return pred == 'false'

def match_str(s:str, rule: str):
    regex = re.compile(rule)

    if regex.fullmatch(s):
        return True
    return False


def match_str_with_re_rules(s:str, rules: List[str]):
    for rule in rules:
        if match_str(s, rule):
            return True
    return False
    