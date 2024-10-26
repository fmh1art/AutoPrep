import re, unicodedata
from dateutil import parser
import pandas as pd
from fuzzywuzzy import fuzz
from nltk import word_tokenize

from dataprep.clean import clean_headers, clean_text
import global_values as GV

from Levenshtein import ratio

def check_similarity(df, row1, row2, threshold=GV.TYPE_DEDUCE_RATIO):
    return all(
        ratio(str(row1[attr]), str(row2[attr])) > threshold for attr in df.columns
    )

# 
def get_all_similar_pairs(df, threshold=GV.TYPE_DEDUCE_RATIO):

    # Find all pairs of records with similarity above 0.9 for all attributes
    similar_pairs = []
    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            if check_similarity(df, df.iloc[i], df.iloc[j], threshold):
                # Create a new DataFrame with the pair of similar records
                pair_df = pd.DataFrame([df.iloc[i], df.iloc[j]])
                similar_pairs.append(pair_df)
    return similar_pairs


def replace_common_special_chars(s: str):
    return s.replace("-", "-")


def filter_special_chars(s):
    return re.sub(r"[^\w\s]", "", s)


def clean_str(x):
    # return x.strip().lower().strip('\'').strip('\"').strip('.').strip()
    if not isinstance(x, str):
        x = x.decode("utf8", errors="ignore")
    # Remove diacritics
    x = "".join(
        c for c in unicodedata.normalize("NFKD", x) if unicodedata.category(c) != "Mn"
    )
    # Normalize quotes and dashes
    x = re.sub(r"[‘’´`]", "'", x)
    x = re.sub(r"[“”]", '"', x)
    x = re.sub(r"[‐‑‒-—−]", "-", x)
    while True:
        old_x = x
        # Remove citations
        x = re.sub(r"((?<!^)\[[^\]]*\]|\[\d+\]|[•♦†‡*#+])*$", "", x.strip())
        # Remove details in parenthesis
        x = re.sub(r"(?<!^)( \([^)]*\))*$", "", x.strip())
        # Remove outermost quotation mark
        x = re.sub(r'^"([^"]*)"$', r"\1", x.strip())
        if x == old_x:
            break
    # Remove final '.'
    if x and x[-1] == ".":
        x = x[:-1]
    # Collapse whitespaces and convert to lower case
    x = re.sub(r"\s+", " ", x, flags=re.U).lower().strip()
    return x


def standardize_val(val):
    val = str(val)
    if is_float(val):
        return str(my_float(val))
    if is_date(val):
        return str(my_date(val, format="%Y-%m-%d %H:%M:%S"))
    return str(val)


def get_date_format(df, col):
    date_eles = {k: [] for k in ["year", "month", "day", "hour", "minute", "second"]}
    for val in df[col].unique():
        if not is_date(val):
            continue
        d = parser.parse(val)
        date_eles["year"].append(d.year)
        date_eles["month"].append(d.month)
        date_eles["day"].append(d.day)
        date_eles["hour"].append(d.hour)
        date_eles["minute"].append(d.minute)
        date_eles["second"].append(d.second)

    key_include = {
        "date": [],
        "time": [],
    }
    for k in date_eles:
        if len(set(date_eles[k])) > 1:
            if k in ["year", "month", "day"]:
                key_include["date"].append(k)
            else:
                key_include["time"].append(k)

    format_dic = {
        "year": "%Y",
        "month": "%m",
        "day": "%d",
        "hour": "%H",
        "minute": "%M",
        "second": "%S",
    }

    date_format = "%Y-%m-%d"
    time_format = "%H:%M:%S"

    if len(key_include["date"]) == 0:
        date_format = ""
    elif len(key_include["date"]) <= 2:
        if "month" not in key_include["date"]:
            key_include["date"].append("month")
        date_format = "-".join(
            [
                format_dic[k]
                for k in ["year", "month", "day"]
                if k in key_include["date"]
            ]
        )

    if len(key_include["time"]) == 0:
        time_format = ""
    elif len(key_include["time"]) == 1:
        k = key_include["time"][0]
        time_format = f"{k}: {format_dic[k]}"
    else:
        if "minute" not in key_include["time"]:
            key_include["time"].append("minute")
        time_format = ":".join(
            [
                format_dic[k]
                for k in ["hour", "minute", "second"]
                if k in key_include["time"]
            ]
        )

    if date_format != "" and time_format != "":
        return f"{date_format} {time_format}"
    elif date_format != "" and time_format == "":
        return date_format
    elif time_format != "" and date_format == "":
        return "%H:%M:%S"
    else:
        return "%Y-%m-%d"


def date_ratio(tbl: pd.DataFrame, column_name: str):
    cnt = 0
    for val in tbl[column_name]:
        try:
            my_date(val)
            cnt += 1
        except:
            continue
    return float(cnt) / (len(tbl) + 1e-6)


def numerical_ratio(tbl: pd.DataFrame, column_name: str):
    cnt = 0
    for val in tbl[column_name]:
        # if is NaN, skip
        if pd.isna(val):
            continue

        try:
            my_float(val)
            cnt += 1
        except:
            continue
    return float(cnt) / (len(tbl) + 1e-6)


def standardize_to_numerical(df: pd.DataFrame, col: str):

    for val in df[col].unique():
        if "[n.a.]" in val:
            continue
        if is_float(val):
            new_val = my_float(val)
        else:
            new_val = str(val) + "[n.a.]"  #!

        # update the value
        df[col] = df[col].replace(val, new_val)

    return df



def _parse_symbol_elements(format_str):

    date_elememts, time_elements = [], []
    for i in range(len(format_str)):
        if format_str[i] == "%":
            if i < len(format_str) - 1:
                ele = format_str[i + 1]
                if ele in GV.DATE_SYMBOLS_SORT:
                    date_elememts.append(ele)
                if ele in GV.TIME_SYMBOLS_SORT:
                    time_elements.append(ele)
    return date_elememts, time_elements


def _get_new_format(original_format):

    date_elememts, time_elements = _parse_symbol_elements(original_format)
    if "y" in date_elememts:
        date_elememts.remove("y")
        date_elememts.append("Y")
    if "b" in date_elememts:
        date_elememts.remove("b")
        date_elememts.append("m")
    if "B" in date_elememts:
        date_elememts.remove("B")
        date_elememts.append("m")

    date_elememts = sorted(date_elememts, key=lambda x: GV.DATE_SYMBOLS_SORT.index(x))
    time_elements = sorted(time_elements, key=lambda x: GV.TIME_SYMBOLS_SORT.index(x))
    date_format = "-".join([f"%{ele}" for ele in date_elememts])
    time_format = ":".join([f"%{ele}" for ele in time_elements if ele in "HIMS"])
    if "p" in time_elements:
        time_format = "%p " + time_format
    if "f" in time_elements:
        time_format = time_format + ".%f"
    if "a" in time_elements:
        time_format = time_format + " %a"
    if "A" in time_elements:
        time_format = time_format + " %A"

    if date_format != "" and time_format != "":
        return f"{date_format} {time_format}"
    elif date_format != "" and time_format == "":
        return date_format
    elif time_format != "" and date_format == "":
        return time_format
    else:
        return "%Y-%m-%d %H:%M:%S"

def standardize_note(value:str):
    if value.count(":") == 0:
        if '.' in value and len(value.split('.')[0]) == 1:
            value = '0' + value
        return '0:' + value
    else:
        return value

def standardize_to_date(df: pd.DataFrame, col: str, ret_format=None):

    if ret_format is None:
        format = get_date_format(df, col)
    else:
        format = ret_format

    date_elememts, time_elements = _parse_symbol_elements(format)

    # skip format like %M:%S.%f
    if len(date_elememts) == 0 and 'f' in format:
        is_note = True
    else:
        is_note = False

    new_format = _get_new_format(format)

    for val in df[col].unique():
        val = str(val)
        if "[n.a.]" in val:
            continue
        if is_date(val):
            if is_note:
                # new_val = standardize_note(val)
                new_val = val
            else:
                try:
                    from datetime import datetime
                    datetime_obj = datetime.strptime(val, format)
                except:
                    datetime_obj = my_date(value=val)

                new_val = datetime_obj.strftime(new_format)
        else:
            new_val = str(val) + "[n.a.]"

        # update the value
        df[col] = df[col].replace(val, new_val)

    return df


def _base_clean_columns(df: pd.DataFrame):
    df.columns = [
        str(col).replace("$", " dollar ").replace("–", "-").replace('\\n', '_') for col in df.columns
    ]
    df = clean_headers(df, remove_accents=True, replace=GV.SPECIAL_CHAR_DICT)
    # if column name is empty, replace it with 'col_i'
    i = 1
    for col in df.columns:
        if col == "" or col.isspace():
            df.rename(columns={col: f"col_{i}"}, inplace=True)
            i += 1
    return df


def _base_clean_values(df: pd.DataFrame):
    custom_pipeline = [
        {"operator": "fillna", "parameters": {"value": "[n.a.]"}},
        {"operator": "lowercase"},
        {"operator": "replace_text", "parameters": {"value": {"–": "-", " ": " ", "ª": "a"}}},
        {"operator": "remove_accents"},
        {"operator": "remove_whitespace"},
    ]

    for col in df.columns:
        # replace \n into \\n
        df[col] = df[col].apply(lambda x: str(x).replace("\n", "<br>") if '\n' in str(x) else x)
        df[col] = df[col].apply(lambda x: str(x).strip("\\").strip('\\""'))
        # replace nan to [n.a.]
        df[col] = df[col].apply(lambda x: "[n.a.]" if 'nan' == str(x).lower() else x)
        df = clean_text(df, col, pipeline=custom_pipeline)

    return df


def base_clean_dataframe(df: pd.DataFrame, colname_cleaning=True, value_cleaning=True, value_standardization=False):
    if colname_cleaning:
        # column name cleaning
        df = _base_clean_columns(df)

    if value_cleaning:
        # table values cleaning
        df = _base_clean_values(df)

    col_types = {col: "string" for col in df.columns}

    if value_standardization:
        # value standardization
        df, col_types = standardization(df)

    return df, col_types


def standardization(df: pd.DataFrame):
    col_trans = {}
    for col in df.columns:
        num_rat = numerical_ratio(df, col)
        if num_rat > GV.GV.TYPE_DEDUCE_RATIO:
            # try to convert the column to numerical
            df = standardize_to_numerical(df, col)
            col_trans[col] = "numerical"
            continue
        col_trans[col] = "string"

    return df, col_trans


def my_date(value, format="%Y-%m-%d %H:%M:%S"):
    value = str(value)

    if len(value) <= 4:
        if "th" in value or "st" in value or "rd" in value or "nd" in value:
            raise ValueError(f"Cannot convert {value} to date")

    if value.lower().strip() in GV.WEEKDAY_DIC:
        raise ValueError(f"Cannot convert {value} to date")

    if value.count("-") == 1:
        fir, sec = value.split("-")
        if str(fir) == str(int(fir)) and str(sec) == str(int(sec)):
            raise ValueError(f"Cannot convert {value} to date")

    try:
        # 
        date_obj = parser.parse(value)
        # if CURRENT_YEAR in ret:
        #     ret = ret.replace(CURRENT_YEAR, DATASET_YEAR)
        return date_obj

    except ValueError:
        raise ValueError(f"Cannot convert {value} to date")


def is_date(value):
    
    try:
        my_date(value)
        return True
    except ValueError:
        return False


def is_float(value):
    try:
        my_float(value)
        return True
    except ValueError:
        return False


def my_float(value):
    if value == "nan":
        raise ValueError(f"Cannot convert {value} to float")
    try:
        value = str(value).replace(",", "")
        if (
            value.endswith("st")
            or value.endswith("nd")
            or value.endswith("rd")
            or value.endswith("th")
        ):
            value = value[:-2].strip()

        ret = float(value)
        # if ret is integer
        if ret.is_integer():
            return int(ret)
        else:
            return ret
    except ValueError:
        raise ValueError(f"Cannot convert {value} to float")

def finditer(sub_str: str, mother_str: str):
    result = []
    start_index = 0
    while True:
        start_index = mother_str.find(sub_str, start_index, -1)
        if start_index == -1:
            break
        end_idx = start_index + len(sub_str)
        # if the last char or the next char is a letter or _, then continue
        if (
            start_index > 0
            and (mother_str[start_index - 1].isalpha() or mother_str[start_index - 1] == "_")
        ) or (
            end_idx < len(mother_str)
            and (mother_str[end_idx].isalpha() or mother_str[end_idx] == "_" or mother_str[end_idx].isnumeric())
        ):
            start_index = end_idx
            continue

        result.append((start_index, end_idx))
        start_index = end_idx
    return result

def basic_fix(sql_str, all_headers, table_title=None, mark='`'):

    if table_title:
        sql_str = sql_str.replace("FROM " + table_title, "FROM w")
        sql_str = sql_str.replace("FROM " + table_title.lower(), "FROM w")

    """Case 1: Fix the `` missing. """
    # Remove the null header.
    while "" in all_headers:
        all_headers.remove("")

    # Remove the '\n' in header.
    # This is because the WikiTQ won't actually show the str in two lines,
    # they use '\n' to mean that, and display it in the same line when print.
    # sql_str = sql_str.replace("\\n", "\n")
    # sql_str = sql_str.replace("\n", "\\n")

    # Add `` in SQL.

    all_headers.sort(key=lambda x: len(x), reverse=True)
    have_matched = [0 for i in range(len(sql_str))]

    # match quotation
    idx_s_single_quotation = [
        _
        for _ in range(1, len(sql_str))
        if sql_str[_] in ["'"] and sql_str[_ - 1] not in ["'"]
    ]
    idx_s_double_quotation = [
        _
        for _ in range(1, len(sql_str))
        if sql_str[_] in ['"'] and sql_str[_ - 1] not in ['"']
    ]
    for idx_s in [idx_s_single_quotation, idx_s_double_quotation]:
        if len(idx_s) % 2 == 0:
            for idx in range(int(len(idx_s) / 2)):
                start_idx = idx_s[idx * 2]
                end_idx = idx_s[idx * 2 + 1]
                have_matched[start_idx:end_idx] = [
                    2 for _ in range(end_idx - start_idx)
                ]

    # match headers
    matched_headers = []
    for header in all_headers:
        if (header in sql_str) and (header not in GV.ALL_KEY_WORDS):
            all_matched_of_this_header = finditer(header, sql_str)
            if len(all_matched_of_this_header) == 0:
                continue
            matched_headers.append(header)
            for matched_of_this_header in all_matched_of_this_header:
                start_idx, end_idx = matched_of_this_header
                if (
                    all(have_matched[start_idx:end_idx]) == 0
                    and (not sql_str[start_idx - 1] == mark)
                    and (not sql_str[end_idx] == mark)
                ):
                    have_matched[start_idx:end_idx] = [
                        1 for _ in range(end_idx - start_idx)
                    ]
                    # a bit ugly, but anyway.

    # re-compose sql from the matched idx.
    start_have_matched = [0] + have_matched
    end_have_matched = have_matched + [0]
    start_idx_s = [
        idx - 1
        for idx in range(1, len(start_have_matched))
        if start_have_matched[idx - 1] == 0 and start_have_matched[idx] == 1
    ]
    end_idx_s = [
        idx
        for idx in range(len(end_have_matched) - 1)
        if end_have_matched[idx] == 1 and end_have_matched[idx + 1] == 0
    ]
    assert len(start_idx_s) == len(end_idx_s)
    spans = []
    current_idx = 0
    for start_idx, end_idx in zip(start_idx_s, end_idx_s):
        spans.append(sql_str[current_idx:start_idx])
        spans.append(sql_str[start_idx : end_idx + 1])
        current_idx = end_idx + 1
    spans.append(sql_str[current_idx:])
    sql_str = mark.join(spans)

    return sql_str, matched_headers


def fuzzy_match_process(sql_str, df, verbose=False):
    """
    Post-process SQL by fuzzy matching value with table contents.
    """

    def _get_matched_cells(value_str, df, fuzz_threshold=70):
        """
        Get matched table cells with value token.
        """
        matched_cells = []
        for row_id, row in df.iterrows():
            for cell in row:
                cell = str(cell)
                fuzz_score = fuzz.ratio(value_str, cell)
                if fuzz_score == 100:
                    matched_cells = [(cell, fuzz_score)]
                    return matched_cells
                if fuzz_score >= fuzz_threshold:
                    matched_cells.append((cell, fuzz_score))

        matched_cells = sorted(matched_cells, key=lambda x: x[1], reverse=True)
        return matched_cells

    def _check_valid_fuzzy_match(value_str, matched_cell):
        """
        Check if the fuzzy match is valid, now considering:
        1. The number/date should not be disturbed, but adding new number or deleting number is valid.
        """
        number_pattern = "[+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?"
        numbers_in_value = re.findall(number_pattern, value_str)
        numbers_in_matched_cell = re.findall(number_pattern, matched_cell)
        try:
            numbers_in_value = [
                float(num.replace(",", "")) for num in numbers_in_value
            ]
        except:
            print(
                f"Can't convert number string {numbers_in_value} into float in _check_valid_fuzzy_match()."
            )
        try:
            numbers_in_matched_cell = [
                float(num.replace(",", "")) for num in numbers_in_matched_cell
            ]
        except:
            print(
                f"Can't convert number string {numbers_in_matched_cell} into float in _check_valid_fuzzy_match()."
            )
        numbers_in_value = set(numbers_in_value)
        numbers_in_matched_cell = set(numbers_in_matched_cell)

        if numbers_in_value.issubset(
            numbers_in_matched_cell
        ) or numbers_in_matched_cell.issubset(numbers_in_value):
            return True
        else:
            return False

    # Drop trailing '\n```', a pattern that may appear in Codex SQL generation
    sql_str = sql_str.rstrip("```").rstrip("\n")

    # Replace QA module with placeholder
    qa_pattern = "MAP\(.+?;.*?`.+?`.*?\)"
    qas = re.findall(qa_pattern, sql_str)
    for idx, qa in enumerate(qas):
        sql_str = sql_str.replace(qa, f"placeholder{idx}")

    # Parse and replace SQL value with table contents
    sql_tokens = tokenize(sql_str)
    sql_template_tokens = extract_partial_template_from_sql(sql_str)
    # Fix 'between' keyword bug in parsing templates
    fixed_sql_template_tokens = []
    sql_tok_bias = 0
    for idx, sql_templ_tok in enumerate(sql_template_tokens):
        sql_tok = sql_tokens[idx + sql_tok_bias]
        if sql_tok == "between" and sql_templ_tok == "[WHERE_OP]":
            fixed_sql_template_tokens.extend(["[WHERE_OP]", "[VALUE]", "and"])
            sql_tok_bias += 2  # pass '[VALUE]', 'and'
        else:
            fixed_sql_template_tokens.append(sql_templ_tok)
    sql_template_tokens = fixed_sql_template_tokens
    for idx, tok in enumerate(sql_tokens):
        if tok in GV.ALL_KEY_WORDS:
            sql_tokens[idx] = tok.upper()

    if verbose:
        print(sql_tokens)
        print(sql_template_tokens)

    assert len(sql_tokens) == len(sql_template_tokens)
    value_indices = [
        idx
        for idx in range(len(sql_template_tokens))
        if sql_template_tokens[idx] == "[VALUE]"
    ]
    for value_idx in value_indices:
        # Skip the value if the where condition column is QA module
        if value_idx >= 2 and sql_tokens[value_idx - 2].startswith("placeholder"):
            continue
        value_str = sql_tokens[value_idx]
        # Drop \"\" for fuzzy match
        is_string = False
        if value_str[0] == '"' and value_str[-1] == '"':
            value_str = value_str[1:-1]
            is_string = True
        # If already fuzzy match, skip
        if value_str[0] == "%" or value_str[-1] == "%":
            continue
        value_str = value_str.lower()
        # Fuzzy Match
        matched_cells = _get_matched_cells(value_str, df)

        if verbose:
            print(matched_cells)

        new_value_str = value_str
        if matched_cells:
            # new_value_str = matched_cells[0][0]
            for matched_cell, fuzz_score in matched_cells:
                if _check_valid_fuzzy_match(value_str, matched_cell):
                    new_value_str = matched_cell
                    if verbose and new_value_str != value_str:
                        print(
                            "\tfuzzy match replacing!",
                            value_str,
                            "->",
                            matched_cell,
                            f"fuzz_score:{fuzz_score}",
                        )
                    break
        if is_string:
            new_value_str = f'"{new_value_str}"'
        sql_tokens[value_idx] = new_value_str
    # Compose new sql string
    # Clean column name in SQL since columns may have been tokenized in the postprocessing, e.g., (ppp) -> ( ppp )
    new_sql_str = " ".join(sql_tokens)
    sql_columns = re.findall("`\s(.*?)\s`", new_sql_str)
    for sql_col in sql_columns:
        matched_columns = []
        for col in df.columns:
            score = fuzz.ratio(sql_col.lower(), col)
            if score == 100:
                matched_columns = [(col, score)]
                break
            if score >= 80:
                matched_columns.append((col, score))
        matched_columns = sorted(matched_columns, key=lambda x: x[1], reverse=True)
        if matched_columns:
            matched_col = matched_columns[0][0]
            new_sql_str = new_sql_str.replace(f"` {sql_col} `", f"`{matched_col}`")
        else:
            new_sql_str = new_sql_str.replace(f"` {sql_col} `", f"`{sql_col}`")

    # Restore QA modules
    for idx, qa in enumerate(qas):
        new_sql_str = new_sql_str.replace(f"placeholder{idx}", qa)

    # Fix '<>' when composing the new sql
    new_sql_str = new_sql_str.replace("< >", "<>")

    return new_sql_str

def post_process_sql(
    sql_str,
    df,
    table_title=None,
    process_program_with_fuzzy_match_on_db=True,
    verbose=False,
    mark='`'
):
    """Post process SQL: including basic fix and further fuzzy match on cell and SQL to process"""

    sql_str, matched_headers = basic_fix(sql_str, list(df.columns), table_title, mark=mark)

    if process_program_with_fuzzy_match_on_db:
        try:
            sql_str = fuzzy_match_process(sql_str, df, verbose)
        except:
            pass

    return sql_str, matched_headers


def extract_partial_template_from_sql(sql, schema={}):
    toks = tokenize(sql)
    # print(toks)
    template = []
    # ignore_follow_up_and = False
    len_ = len(toks)
    idx = 0
    while idx < len_:
        tok = toks[idx]
        if tok == "from":
            template.append(tok)
            if toks[idx + 1] != "(":
                # template.append("[FROM_PART]")
                idx += 1
                while idx < len_ and (
                    toks[idx] not in GV.CLAUSE_KEYWORDS and toks[idx] != ")"
                ):
                    template.append(toks[idx])
                    idx += 1
                continue
        elif tok in GV.CLAUSE_KEYWORDS:
            template.append(tok)
        elif tok in GV.AGG_OPS:
            template.append(tok)
        elif tok in [",", "*", "(", ")", "having", "by", "distinct"]:
            template.append(tok)
        elif tok in ["asc", "desc"]:
            template.append("[ORDER_DIRECTION]")
        elif tok in GV.WHERE_OPS:
            if tok in GV.KEPT_WHERE_OP:
                template.append(tok)
            else:
                template.append("[WHERE_OP]")
                if tok == "between":
                    idx += 2
        elif tok in GV.COND_OPS:
            template.append(tok)
        elif template[-1] == "[WHERE_OP]":
            template.append("[VALUE]")
        elif template[-1] == "limit":
            template.append("[LIMIT_VALUE]")
        else:
            template.append(tok)
        idx += 1
    return template


def tokenize(string):
    string = str(string)
    string = string.replace(
        "'", '"'
    )  # ensures all string values wrapped by "" problem??
    quote_idxs = [idx for idx, char in enumerate(string) if char == '"']
    assert len(quote_idxs) % 2 == 0, "Unexpected quote"

    # keep string value as token
    vals = {}
    for i in range(len(quote_idxs) - 1, -1, -2):
        qidx1 = quote_idxs[i - 1]
        qidx2 = quote_idxs[i]
        val = string[qidx1 : qidx2 + 1]
        key = "__val_{}_{}__".format(qidx1, qidx2)
        string = string[:qidx1] + key + string[qidx2 + 1 :]
        vals[key] = val

    # tokenize sql
    toks_tmp = [word.lower() for word in word_tokenize(string)]
    toks = []
    for tok in toks_tmp:
        if tok.startswith("=__val_"):
            tok = tok[1:]
            toks.append("=")
        toks.append(tok)

    # replace with string value token
    for i in range(len(toks)):
        if toks[i] in vals:
            toks[i] = vals[toks[i]]

    # find if there exists !=, >=, <=
    eq_idxs = [idx for idx, tok in enumerate(toks) if tok == "="]
    eq_idxs.reverse()
    prefix = ("!", ">", "<")
    for eq_idx in eq_idxs:
        pre_tok = toks[eq_idx - 1]
        if pre_tok in prefix:
            toks = toks[: eq_idx - 1] + [pre_tok + "="] + toks[eq_idx + 1 :]

    return toks
