from flask import Flask, request, jsonify, send_from_directory
from ddgs import DDGS
from google import genai

app = Flask(__name__)
client = genai.Client()  # reads GEMINI_API_KEY

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/ask", methods=["POST"])
def ask():
    question = (request.json or {}).get("question", "").strip()
    if not question:
        return jsonify(answer="Please type a question.", sources=[])
    try:
        results = DDGS().text(question, max_results=6)
    except Exception:
        results = []
    if not results:
        return jsonify(answer="I couldn't find sources for that. Try rephrasing.", sources=[])

    context = "\n\n".join(
        f"[{i+1}] {r['title']}\n{r['body']}" for i, r in enumerate(results)
    )
    prompt = (
        "Answer the question using ONLY the sources below. "
        "If they don't contain the answer, say you're not sure.\n\n"
        f"Sources:\n{context}\n\nQuestion: {question}"
    )
    try:
        resp = client.models.generate_content(
            model="gemini-flash-latest", contents=prompt
        )
        answer = resp.text
    except Exception:
        answer = "The AI is busy right now. Please try again in a minute."
    sources = [{"url": r["href"], "title": r["title"]} for r in results]
    return jsonify(answer=answer, sources=sources)
