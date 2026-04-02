from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from flask import Blueprint, Response, jsonify, request

from backend.models.model import ModelManager
from backend.data.chatlog import store_chat_log, read_chat_log
from backend.soul_extracter.request import extract_soul
from backend.data.prompt_loader import load_prompt


model_manager = ModelManager.get_instance()

model = model_manager.get_model()

gateway = Blueprint("gateway", __name__)

_souls: dict[str, dict] = {}
_sessions: dict[str, dict] = {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ok(data, status_code: int = 200):
    return jsonify({"ok": True, "data": data}), status_code


def _err(code: str, message: str, status_code: int = 400):
    return jsonify({"ok": False, "error": {"code": code, "message": message}}), status_code


@gateway.post("/api/chatlogs/parse")
def parse_chatlogs(bro_name: str | None = None, type: str | None = None, payload: str | None = None, options: dict | None = None):
    body = request.get_json(silent=True) or {}

    bro_name = body.get("bro_name") or bro_name or None
    if not bro_name:
        return _err("INVALID_ARGUMENT", "缺少 bro_name", 400)

    type = body.get("type") or type or None
    payload = body.get("payload") or payload or None
    if not type or not payload:
        return _err("INVALID_ARGUMENT", "缺少 type 或 payload", 400)

    if type == 'txt':
        store_chat_log(bro_name, payload)
        
    return _ok(
        {
            "bro_name": bro_name,
            "type": type,
        }
    )


@gateway.post("/api/souls/distill")
def distill_soul(bro_name: str | None = None):
    body = request.get_json(silent=True) or {}
    
    bro_name = body.get("bro_name") or bro_name or None
    if not bro_name:
        return _err("INVALID_ARGUMENT", "缺少 bro_name", 400)

    chatlog = read_chat_log(bro_name)
    if not chatlog:
        return _err("NOT_FOUND", "此人的聊天记录不存在", 404)

    meta_prompt = load_prompt("MetaPrompt.md")
    prompt = f"你接下来要分析好兄弟的聊天记录，提取出记录中好兄弟的SOUL。其中，好兄弟的名字是**{bro_name}**。\n{meta_prompt}\n对话记录为：\n{chatlog}"

    response = model.generate(prompt)

    return _ok({"bro_name": bro_name, "soul_markdown": response})


@gateway.post("/api/souls/save")
def save_soul(bro_name: str | None = None, soul_markdown: str | None = None):
    body = request.get_json(silent=True) or {}
    bro_name = body.get("bro_name") or bro_name
    soul_markdown = body.get("soul_markdown") or soul_markdown or ""
    if not bro_name:
        return _err("INVALID_ARGUMENT", "缺少 bro_name", 400)

    created_at = _now_iso()
    _souls[bro_name] = {"bro_name": bro_name, "created_at": created_at, "soul_markdown": soul_markdown}
    return _ok({"path": f"souls/{bro_name}_SOUL.md"})


@gateway.get("/api/souls")
def list_souls():
    data = [{"bro_name": v["bro_name"], "created_at": v["created_at"]} for v in _souls.values()]
    return _ok(data)


@gateway.get("/api/souls/<string:bro_name>")
def get_soul(bro_name: str):
    soul = _souls.get(bro_name)
    if not soul:
        return _err("NOT_FOUND", "SOUL 不存在", 404)
    return _ok({"bro_name": bro_name, "soul_markdown": soul.get("soul_markdown", "")})


@gateway.get("/api/souls/<string:bro_name>/export")
def export_soul(bro_name: str):
    soul = _souls.get(bro_name)
    if not soul:
        return _err("NOT_FOUND", "SOUL 不存在", 404)

    content = soul.get("soul_markdown", "")
    response = Response(content, mimetype="text/markdown; charset=utf-8")
    response.headers["Content-Disposition"] = f'attachment; filename="{bro_name}_SOUL.md"'
    return response


@gateway.delete("/api/souls/<string:bro_name>")
def delete_soul(bro_name: str):
    if bro_name not in _souls:
        return _err("NOT_FOUND", "SOUL 不存在", 404)
    del _souls[bro_name]
    return _ok({"deleted": True})


@gateway.post("/api/sessions")
def create_session(session_id: str | None = None):
    body = request.get_json(silent=True) or {}
    bro_name = body.get("bro_name") or "unknown"
    session_id = body.get("session_id") or session_id or uuid4().hex
    created_at = _now_iso()
    session = {
        "id": session_id,
        "bro_name": bro_name,
        "created_at": created_at,
        "last_message_at": created_at,
        "chat_history": [],
    }
    _sessions[session_id] = session
    return _ok({"id": session_id, "bro_name": bro_name, "chat_history": []})


@gateway.get("/api/sessions")
def list_sessions():
    data = [
        {
            "id": v["id"],
            "bro_name": v["bro_name"],
            "created_at": v["created_at"],
            "last_message_at": v["last_message_at"],
        }
        for v in _sessions.values()
    ]
    return _ok(data)


@gateway.get("/api/sessions/<string:session_id>")
def get_session(session_id: str):
    session = _sessions.get(session_id)
    if not session:
        return _err("NOT_FOUND", "Session 不存在", 404)
    return _ok({"id": session["id"], "bro_name": session["bro_name"], "chat_history": session["chat_history"]})


@gateway.post("/api/sessions/<string:session_id>/messages")
def create_session_message(session_id: str, user_msg: str | None = None):
    session = _sessions.get(session_id)
    if not session:
        return _err("NOT_FOUND", "Session 不存在", 404)

    body = request.get_json(silent=True) or {}
    message = body.get("message") or body.get("user_msg") or user_msg
    if not message:
        return _err("INVALID_ARGUMENT", "缺少 message/user_msg", 400)

    session["chat_history"].append({"role": "user", "content": message})
    session["chat_history"].append({"role": "assistant", "content": f"（占位回复）你刚才说：{message}"})
    session["last_message_at"] = _now_iso()
    return _ok({"chat_history": session["chat_history"]})


@gateway.delete("/api/sessions/<string:session_id>")
def delete_session(session_id: str):
    if session_id not in _sessions:
        return _err("NOT_FOUND", "Session 不存在", 404)
    del _sessions[session_id]
    return _ok({"deleted": True})
