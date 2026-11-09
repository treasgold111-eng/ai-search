from flask import Flask, request, jsonify, send_from_directory
import anthropic

app = Flask(__name__)
client = anthropic.Anthropic()

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/ask", methods=["POST"])
def ask():
    question = request.json.get("question", "")
    response = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=1500,
        system="Answer using web search. Be accurate. "
               "If you can't verify something, say so.",
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": question}],
    )
    answer, sources = "", {}
    for block in response.content:
        if block.type == "text":
            answer += block.text
            for c in (getattr(block, "citations", None) or []):
                sources[c.url] = c.title
    return jsonify(
        answer=answer,
        sources=[{"url": u, "title": t} for u, t in sources.items()],
    )
