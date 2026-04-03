from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from flask import Blueprint, Response, jsonify, request

from backend.models.model import ModelManager
from backend.data.chatlog import store_chat_log, read_chat_log
from backend.data.prompt_loader import load_prompt
from backend.data.soul import store_soul, read_soul, view_soul, remove_soul, export_soul_markdown
from backend.data.session import Session, new_session, view_session, remove_session


model_manager = ModelManager.get_instance()

model = model_manager.get_model()

gateway = Blueprint("gateway", __name__)

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

    if type == 'db':
        store_chat_log(bro_name, payload)
    elif type == 'txt':
        store_chat_log(bro_name, payload)
        
    messages_count = len([line for line in str(payload).splitlines() if line.strip()])
    return _ok(
        {
            "bro_name": bro_name,
            "type": type,
            "messages_count": messages_count,
            "participants": [bro_name],
            "parsed_at": _now_iso(),
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
    if not bro_name or not soul_markdown:
        return _err("INVALID_ARGUMENT", "缺少 bro_name 或 soul_markdown", 400)

    created_at = _now_iso()
    safe_name = store_soul(bro_name, soul_markdown, created_at)
    return _ok({"path": f"souls/{safe_name}.md", "created_at": created_at})


@gateway.get("/api/souls")
def list_souls():
    souls = view_soul()
    return _ok([{"bro_name": bro_name, "created_at": created_at} for bro_name, created_at in souls])


@gateway.get("/api/souls/<string:bro_name>")
def get_soul(bro_name: str):
    soul_markdown = read_soul(bro_name)
    if soul_markdown is None:
        return _err("NOT_FOUND", "SOUL 不存在", 404)
    return _ok({"bro_name": bro_name, "soul_markdown": soul_markdown})


@gateway.get("/api/souls/<string:bro_name>/export")
def export_soul(bro_name: str):
    exported = export_soul_markdown(bro_name)
    if exported is None:
        return _err("NOT_FOUND", "SOUL 不存在", 404)
    file_name, content = exported

    response = Response(content, mimetype="text/markdown; charset=utf-8")
    response.headers["Content-Disposition"] = f'attachment; filename="{file_name}"'
    return response


@gateway.delete("/api/souls/<string:bro_name>")
def delete_soul(bro_name: str):
    if not remove_soul(bro_name):
        return _err("NOT_FOUND", "SOUL 不存在", 404)
    return _ok({"deleted": True})


@gateway.post("/api/sessions")
def create_session(session_id: str | None = None):
    body = request.get_json(silent=True) or {}
    bro_name = body.get("bro_name") or "BRO"
    session_id = body.get("session_id") or session_id or uuid4().hex
    created_at = _now_iso()
    new_session(session_id, bro_name, created_at)
    return _ok({"id": session_id, "bro_name": bro_name, "chat_history": []})


@gateway.get("/api/sessions")
def list_sessions():
    sessions = view_session()
    return _ok(
        [
            {
                "id": session_id,
                "bro_name": bro_name,
                "created_at": created_time,
                "last_message_at": created_time,
            }
            for session_id, bro_name, created_time in sessions
        ]
    )


@gateway.get("/api/sessions/<string:session_id>")
def get_session(session_id: str):
    try:
        session = Session(session_id)
    except FileNotFoundError:
        return _err("NOT_FOUND", "Session 不存在", 404)

    chat_history: list[dict[str, str]] = []
    for user_message, bro_message in session.message_list:
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": bro_message})
    return _ok({"id": session.session_id, "bro_name": session.bro_name, "chat_history": chat_history})


@gateway.post("/api/sessions/<string:session_id>/messages")
def create_session_message(session_id: str, user_msg: str | None = None):
    try:
        session = Session(session_id)
    except FileNotFoundError:
        return _err("NOT_FOUND", "Session 不存在", 404)

    body = request.get_json(silent=True) or {}
    message = body.get("message") or body.get("user_msg") or user_msg
    if not message:
        return _err("INVALID_ARGUMENT", "缺少 message/user_msg", 400)

    prompt = session.concatenate_prompt(message)
    bro_reply = model.generate(prompt)
    session.add_message(message, bro_reply)
    session.store()

    chat_history: list[dict[str, str]] = []
    for user_message, bro_message in session.message_list:
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": bro_message})
    return _ok({"chat_history": chat_history})


@gateway.delete("/api/sessions/<string:session_id>")
def delete_session(session_id: str):
    if not remove_session(session_id):
        return _err("NOT_FOUND", "Session 不存在", 404)
    return _ok({"deleted": True})
