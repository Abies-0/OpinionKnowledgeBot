import pandas as pd
import pickle
import re
import string
import yaml
import zhon

def detect_language(text):

    if not text:
        return "en"

    ENGLISH_REQUEST_PATTERN = r"^(who|what|when|where|why|how|could|would|should|can|translate|pronounce|explain|tell|do you know|can you say|how do you say)\b"

    chinese_count = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_count = len(re.findall(r'[a-zA-Z]', text))

    total_length = len(text)

    if re.search(ENGLISH_REQUEST_PATTERN, text, re.IGNORECASE):
        return "en"

    if chinese_count / total_length > 0.1:
        return "zh"
    else:
        return "en"


def extract_string(text):
    punctuation = zhon.hanzi.punctuation + string.punctuation
    pattern = f"[{re.escape(punctuation)}]"
    text_clean = re.sub(pattern, " ", text)
    return text_clean.strip()


def get_config(file_path):
    try:
        with open (file_path, "r", encoding="utf-8") as f:
            data = yaml.load(f, Loader=yaml.CLoader)
        return data
    except Exception as e:
        print(e)
    return {}


def get_csv(file_path):
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        print(e)
    return pd.DataFrame()


def get_pickle(file_path):
    try:
        with open (file_path, "rb") as f:
            data = pickle.load(f)
        return data
    except Exception as e:
        print(e)
    return []