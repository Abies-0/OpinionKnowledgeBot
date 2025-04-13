import os
import re
import pickle

class TextSegmentation:

    def __init__(self, filename, save_file=False):
        self.filename = filename
        self.save_file = save_file

    def fetch_text(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            raw_text = f.read()
        return raw_text

    def make_text_sections(self, text):

        sections = {}
        
        parts = re.split(r'\n(?=# )', text)
        for part in parts:
            lines = part.strip().split('\n', 1)
            title = lines[0].replace("#", "").strip()
            content = lines[1].strip() if len(lines) > 1 else ""
            sections[title] = content

        return sections

    def save_to_pickle(self, content):
        target_dir = "configs"
        os.makedirs(target_dir, exist_ok=True)
        with open (f"{target_dir}/{self.filename.split('.')[0]}.pkl", "wb") as f:
            pickle.dump(content, f)

    def make_segmentation(self):
        raw_text = self.fetch_text(self.filename)
        sections = self.make_text_sections(raw_text)
        
        for k, v in sections.items():
            if not v:
                initial_text = k
        
        sections.pop(initial_text, "")
        texts = []
        texts.append(f"KEYPO平台包含{len(sections)}支API：{'、'.join(list(sections.keys()))}")

        colon = "："
        for k, v in sections.items():
            title = k
            content = v.replace("## 邏輯說明\n", "")
            items = content.split("\n\n")
            if len(items) > 1:
                unit_list, sub_title_list = [], []
                sub_title_list = []
                for idx in range(len(items)):
                    temp_list = items[idx].split("\n\t")
                    sub_list = [text.replace("- ", "") for text in temp_list]
                    sub_title, sub_content = sub_list[0], sub_list[1:]
                    sub_title_list.append(sub_title.replace(colon, ""))
                    sub_title = sub_title if colon == sub_title[-1] else f"{sub_title}{colon}"
                    sub_content_str = " ".join([f"({i+1}) {_sub_content}" for i, _sub_content in enumerate(sub_content)])
                    unit_content = sub_title + sub_content_str
                    unit_list.append(unit_content)
                texts.append(f"[{title}]功能\t{'、'.join(sub_title_list)}")
                for i, c in enumerate(unit_list):
                    texts.append(f"[{title}]\t{c}")
                
            else:
                item_text = "".join(items)
                sub_list = item_text.split("- ")[1:]
                sub_title_list = []
                for idx in range(len(sub_list)):
                    sub_title = sub_list[idx].split(colon)[0]
                    sub_title_list.append(sub_title)
                unit_list = [t.strip() for t in sub_list]
                texts.append(f"[{title}]功能\t{'、'.join(sub_title_list)}")
                for i, c in enumerate(unit_list):
                    texts.append(f"[{title}]\t{c}")

        if self.save_file:
            self.save_to_pickle(texts)

        return texts