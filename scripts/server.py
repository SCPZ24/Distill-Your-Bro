import os
from flask import Flask, jsonify, send_from_directory


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
FRONTEND_DIR = os.path.join(ROOT, "frontend")
DIST_DIR = os.path.join(FRONTEND_DIR, "dist")

app = Flask(
    __name__,
    static_folder=DIST_DIR if os.path.isdir(DIST_DIR) else FRONTEND_DIR,
    template_folder=DIST_DIR if os.path.isdir(DIST_DIR) else FRONTEND_DIR,
)


@app.route("/")
def index():
    base_dir = DIST_DIR if os.path.isdir(DIST_DIR) else FRONTEND_DIR
    index_path = os.path.join(base_dir, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(base_dir, "index.html")
    return (
        "<h1>Distill Your Bro</h1><p>前端未构建：请先执行 make build</p>",
        200,
        {"Content-Type": "text/html; charset=utf-8"},
    )

@app.route("/<path:path>")
def static_proxy(path: str):
    base_dir = DIST_DIR if os.path.isdir(DIST_DIR) else FRONTEND_DIR
    file_path = os.path.join(base_dir, path)
    if os.path.isfile(file_path):
        return send_from_directory(base_dir, path)
    index_path = os.path.join(base_dir, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(base_dir, "index.html")
    return ("Not Found", 404)


@app.route("/api/health")
def health():
    return jsonify({"ok": True, "service": "distill-your-bro", "version": 1})


def main():
    port = int(os.environ.get("PORT", "1007"))
    print(f"Server listening at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)


if __name__ == "__main__":
    main()
