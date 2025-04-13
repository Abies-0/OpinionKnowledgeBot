# 🧠 OpinionKnowledgeBot

**OpinionKnowledgeBot** 是一個結合即時新聞擷取與知識文件檢索的 AI 聊天機器人，具備輿情分析與知識問答能力，支援繁體中文，並整合 LLM 與 RAG 架構。

---

## 🚀 快速啟動

### 🧾 0️⃣ 取得原始碼

```bash
git clone git@github.com:Abies-0/OpinionKnowledgeBot.git
cd OpinionKnowledgeBot
```

### 1️⃣ 安裝依賴套件

```bash
pip install -r requirements.txt
```

建議使用 Python 3.10+

### 2️⃣ 啟動 API Server (目前使用 Flask)

```bash
python app.py
```

預設會在 `http://localhost:8088` 開啟服務。

---

## ⚙️ 設定說明

所有設定統一集中在 `configs/` 資料夾，請依照以下說明修改：

### 🔐 1. OpenAI API Key 設定

請打開：

```bash
configs/llm_config.yml
```

將 `OpenAI` 欄位的 `api_key` 欄位替換為你自己的 OpenAI API 金鑰：

```yaml
api_key: sk-xxx...        # << 請替換成你自己的 key
model: gpt-4o
```

### 🧠 2. Prompt 設定管理

所有與 LLM 溝通的提示語（prompt）皆集中管理於：

```bash
configs/prompts.yml
```

目前已附上簡易版可供參考，可依需求調整。
其中，**VerifyQuestion**、**Summarize**、**BuildReferenceBefore**、**BuildReferenceAfter**為**OpinionBot**的提示詞，**RAG**為**KeyRAGBOT**的提示詞。

### 🌐 3. API Server Port 設定

若需修改 Flask API 的啟動埠（預設為 `8088`），請編輯：

```bash
configs/api_config.yml
```

範例設定：

```yaml
debug: False
host: "0.0.0.0"
port: 8088        # << 請替換成你想要使用的 port
```

---

## 📁 新聞資料儲存位置

OpinionBot 搜尋到的新聞經過處理後，會自動儲存在：

```bash
saved_articles/
```

輸出每篇新聞的**標題**、**日期**、**摘要**、**情緒分析**、**命名實體**、**原始內文**，以方便後續追蹤與除錯。

---

## 📡 API 介面說明

### 🔍 POST `/api/opinion`

接收使用者輿情相關問題，自動查詢新聞並分析回答。

#### 請求格式：

```json
{
  "question": "最近台灣的政治有哪些變動？",
  "seed": 3
}
```
question 為你想要詢問的輿情相關問題，seed 為擷取的新聞篇數(最多 10 篇，考量到效能問題，建議一開始測試設 3 以內)。

#### 回應格式：

```json
{
  "answer": "這是 OpinionBot 回應..."
}
```
answer 為機器人回應，僅回覆與輿情相關問題。

### 📘 POST `/api/keypo`

根據 KEYPO 功能手冊回答相關問題（文件檢索 + LLM 回答）

#### 請求格式：

```json
{
  "question": "KEYPO 的文章列表功能是什麼？"
}
```
question 為你想要詢問的 Keypo 文件相關問題。

#### 回應格式：

```json
{
  "answer": "KEYPO 的文章列表可展示文章標題、摘要、來源..."
}
```
answer 為機器人回應，僅在詢問內容與文件相關時回覆。

---

## 🧪 測試工具：`test_api.py`

你可以使用 CLI 工具快速測試機器人：

```bash
python test_api.py
```

互動輸入後可選擇：

- 輸入 `2`：使用 KeypoRAGBot
- 其他輸入或直接 Enter：使用 OpinionBot（預設）

---

## 🖥 系統相容性與語言支援

- ✅ 支援平台：
  - Windows 10 以上版本
  - Ubuntu 22.04 LTS

- 🌐 查詢語言：
  - 目前僅支援 **繁體中文新聞查詢**

---

## 🛠 TODO（開發中與未來功能）

- [ ] 使用 Multi-Threading 併行處理新聞
- [ ] 整合本地模型使用
- [ ] 支援英文或多國語言
- [ ] 建立前端互動頁面
- [ ] 撰寫 pytest 、建立 CI/CD
- [ ] 建立基於不同 OS 的 Docker Image
