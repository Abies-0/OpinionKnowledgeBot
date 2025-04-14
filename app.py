from flask import Flask, request, jsonify
from opinion_bot import OpinionBot
from keypo_rag_bot import KeypoRAGBot
from utils import get_config

app = Flask(__name__)

opinion_bot = OpinionBot()
print("-- OpinionBot API serve --")
keypo_bot = KeypoRAGBot(filename="KEYPO功能手冊文件.md")
print("-- KeypoRAGBot API serve --")

config = get_config("configs/api_config.yml")

@app.route(config["routes"]["opinion_api"], methods=["POST"])
def opinion_api():
    try:
        data = request.get_json()
        question = data.get("question", "")
        seed = data.get("seed", 10)
        if not question:
            return jsonify({"error": "Missing question field"}), 400
        response = opinion_bot.answer(question, seed)
        return jsonify({"answer": response.get("text", "")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route(config["routes"]["keypo_api"], methods=["POST"])
def keypo_api():
    try:
        data = request.get_json()
        question = data.get("question", "")
        if not question:
            return jsonify({"error": "Missing question field"}), 400
        response = keypo_bot.answer(question)
        return jsonify({"answer": response.get("text", "")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=config["server"]["debug"], host=config["server"]["host"], port=config["server"]["port"])
