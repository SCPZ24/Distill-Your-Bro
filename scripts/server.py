import os
from flask import Flask, send_from_directory, jsonify


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
FRONTEND_DIR = os.path.join(ROOT, "frontend")

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    template_folder=FRONTEND_DIR,
)


@app.route("/")
def index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(FRONTEND_DIR, "index.html")
    return (
        "<h1>Distill Your Bro</h1><p>前端未初始化：缺少 frontend/index.html</p>",
        200,
        {"Content-Type": "text/html; charset=utf-8"},
    )


@app.route("/api/health")
def health():
    return jsonify({"ok": True, "service": "distill-your-bro", "version": 1})


def main():
    port = int(os.environ.get("PORT", "1007"))
    print(f"Dev server listening at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)


if __name__ == "__main__":
    main()

