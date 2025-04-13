import json
import openai
import os
import random
import re
import time
import trafilatura
from ckip_transformers.nlp import CkipNerChunker
from datetime import datetime
from google_news import GoogleNews
from transformers import pipeline
from utils import extract_string, get_config


class OpinionBot:

    def __init__(self):
        self.prompts = get_config("configs/prompts.yml")
        self.llm_model = get_config("configs/llm_config.yml")["OpenAI"]["model"]
        self.sentiment_model = get_config("configs/llm_config.yml")["Sentiment"]["model"]
        self.ner = CkipNerChunker()
        self.sentiment_pipeline  = pipeline("sentiment-analysis", model=self.sentiment_model)
        self.client = openai.OpenAI(api_key=get_config("configs/llm_config.yml")["OpenAI"]["api_key"])

    def get_google_news(self, query, lang="zh-TW"):
        _lang, _region = lang.split("-")
        googlenews = GoogleNews(encode="utf-8", lang=_lang, region=_region)
        googlenews.get_news(query)
        results = googlenews.results(sort=True)
        return results

    def text_generation(self, query, general_output):
        try:
            completion = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {
                        "role": "user",
                        "content": query
                    }
                ]
            )
            raw_text = completion.choices[0].message.content
            result = re.search(r'\{.*\}', raw_text, re.DOTALL).group(0).replace("'", '"')
            return json.loads(result)            
        except Exception as e:
            print(e)
        return general_output


    def fetch_content_from_url(self, url):
        try:
            downloaded = trafilatura.fetch_url(url)
            result = trafilatura.extract(downloaded, include_comments=False, include_images=False, output_format="json")
            return json.loads(result)["text"]
        except Exception as e:
            print(e)
        return ""

    def extract_named_entities(self, text):
        results = self.ner([text])
        entities = set()
        for ent in results[0]:
            entities.add(ent.word)
        return list(entities)

    def analyze_sentiment(self, chunks):
    
        scores, labels = [], []
        for chunk in chunks:
            try:
                result = self.sentiment_pipeline(chunk)[0]
                score = result["score"]
                label = result["label"]
                scores.append(score)
                labels.append(label)
            except Exception as e:
                print(f"[Sentiment Error] {e}")
    
        if not scores:
            return {"label": "neutral", "score": 0.0}
        
        avg_score = sum(scores) / len(scores)
        label_counts = {l: labels.count(l) for l in set(labels)}
        final_label = max(label_counts, key=label_counts.get)
    
        return {
            "label": final_label,
            "score": round(avg_score, 4)
        }

    def make_text_chunks(self, text, max_len=512):
        chunks = []
        chunk = ""
        for char in text:
            chunk += char
            if len(chunk) >= max_len:
                chunks.append(chunk)
                chunk = ""
        if chunk:
            chunks.append(chunk)
        return chunks

    def fetch_news_results(self, all_news, max_seed):
        
        contents = []
        if len(all_news) == 0:
            return contents

        max_seed = min(max_seed, 10)
        seed = random.randint(1, min(len(all_news), max_seed))
        print(f"[Bot]\t將為您擷取{seed}則新聞作回應參考。\n")
        count = 0
        for idx in range(len(all_news)):
            if count == seed:
                break
            try:
                raw_content = self.fetch_content_from_url(all_news[idx]["source"])
                time.sleep(0.5)
            except Exception as e:
                print(e)
                continue
            if not raw_content:
                continue
            else:
                content_summary = self.text_generation(self.prompts["Summarize"].replace("QUERY", raw_content), {"content": "", "summary": ""})
                content = content_summary["content"]
                summary = content_summary["summary"]
                if not content:
                    continue
                text_chunks = self.make_text_chunks(content)
                sentiment_result = self.analyze_sentiment(text_chunks)
                NER = self.extract_named_entities(content)
                if not summary or not sentiment_result or not NER:
                    continue
                count += 1
                contents.append(
                    {
                        "title": all_news[idx]["title"],
                        "date": all_news[idx]["date"],
                        "content": content,
                        "summary": summary,
                        "sentiment_label": sentiment_result["label"],
                        "sentiment_score": sentiment_result["score"],
                        "NER": NER
                    }
                )
                print(f"[Bot]\t** 第{count}則新聞處理完畢 **")
        if count < seed:
            print(f"[Bot]\t因可解析新聞數量不足，僅擷取{count}則新聞。")
        return contents

    def build_reference_prompt(self, user_question, articles):
        
        prompt = [self.prompts["BuildReferenceBefore"].replace("QUERY", user_question.strip())]
        for idx, article in enumerate(articles, 1):
            block = [
                f"[第{idx}則新聞]",
                f"標題：{article['title']}",
                f"日期：{article['date']}",
                f"摘要：{article['summary']}",
                f"情緒分析：{article['sentiment_label']} (score: {round(article['sentiment_score'], 4)})",
                f"命名實體：{', '.join(article['NER'])}",
                ""
            ]
            prompt.extend(block)
    
        prompt.append(self.prompts["BuildReferenceAfter"])
        total_prompt = "\n".join(prompt)
        return total_prompt

    def save_articles_as_markdown(self, articles, folder="saved_articles"):
        os.makedirs(folder, exist_ok=True)
        filename = f"articles_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        filepath = os.path.join(folder, filename)    
        
        lines = []
        for i, article in enumerate(articles, start=1):
            lines.append(f"### 第{i}篇文章 ###\n")
            lines.append(f"**標題：** {article['title']}")
            lines.append(f"**日期：** {article['date']}")
            lines.append(f"**摘要：** {article['summary']}")
            lines.append(f"**情緒分析：** {article['sentiment_label']}（score: {round(article['sentiment_score'], 4)}）")
            lines.append(f"**命名實體：** {', '.join(article['NER'])}")
            lines.append(f"**原始內文：**\n{article['content']}\n")
            lines.append("---\n")  # 分隔線
        markdown = "\n".join(lines)
    
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown)
    
        print(f"[Bot]\t已將新聞儲存為 Markdown：{filepath}\n")

    def answer(self, query, seed=10):
    
        print(f"[User]\t{query}")
        
        opinion_question = self.text_generation(self.prompts["VerifyQuestion"].replace("QUERY", query), {"is_opinion_question": "N", "topics": []})
        if opinion_question["is_opinion_question"].lower() != "y":
            bot_msg = f"\n[Bot]\t您的問題 '{query}' 與輿情沒什麼相關喔，要不要討論其他議題呢？"
            print(bot_msg)
            return {"text": bot_msg}

        if not opinion_question["topics"]:
            clean_query = extract_string(query)
        else:
            clean_query = " ".join(opinion_question["topics"])

        print(f"\n[Bot]\t將使用關鍵字 '{clean_query}' 進行搜索...")
    
        news = self.get_google_news(clean_query)
        news_references = self.fetch_news_results(news, seed)
        self.save_articles_as_markdown(news_references)
    
        total_query = self.build_reference_prompt(query, news_references)
        
        return self.text_generation(total_query, {"text": ""})