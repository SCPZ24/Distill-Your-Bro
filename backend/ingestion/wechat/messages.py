"""从 message_*.db 读取与某 wxid 的单聊消息。"""

from __future__ import annotations

import hashlib
import logging
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

CN_TZ = timezone(timedelta(hours=8))


class WechatMessageRepository:
    """
    表名 Msg_<md5(wxid) hex>，分散在多个 message_N.db 中。
    """

    def __init__(self, db_dir: str) -> None:
        self._db_dir = db_dir

    def find_user_tables(self, wxid: str) -> List[Tuple[str, str]]:
        table_hash = hashlib.md5(wxid.encode("utf-8")).hexdigest()
        table_name = f"Msg_{table_hash}"
        message_dir = os.path.join(self._db_dir, "message")
        if not os.path.isdir(message_dir):
            return []

        results: List[Tuple[str, str]] = []
        for filename in sorted(os.listdir(message_dir)):
            if filename.startswith("message_") and filename.endswith(".db"):
                if "fts" in filename or "resource" in filename:
                    continue
                db_path = os.path.join(message_dir, filename)
                try:
                    conn = sqlite3.connect(db_path)
                    try:
                        exists = conn.execute(
                            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                            (table_name,),
                        ).fetchone()
                        if exists:
                            results.append((db_path, table_name))
                    finally:
                        conn.close()
                except Exception:
                    pass
        return results

    def extract_thread(
        self,
        wxid: str,
        my_name: str = "我",
        friend_display: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if "@chatroom" in wxid:
            raise ValueError(f"'{wxid}' 是群聊，本工具仅支持 1 对 1 单聊。")

        friend_name = friend_display or wxid
        tables = self.find_user_tables(wxid)
        if not tables:
            raise FileNotFoundError(
                f"未找到与 '{wxid}' 的聊天记录。\n"
                "可能原因: wxid 不正确、消息在未解密库中、或确实无记录。"
            )

        messages: List[Dict[str, Any]] = []
        for db_path, table_name in tables:
            conn = sqlite3.connect(db_path)
            try:
                rows = conn.execute(
                    f"""
                    SELECT create_time, local_type, message_content, status
                    FROM [{table_name}]
                    ORDER BY create_time ASC
                    """
                ).fetchall()

                for create_time, local_type, content, status in rows:
                    is_me = status == 2
                    sender = my_name if is_me else friend_name

                    if isinstance(content, bytes):
                        try:
                            content = content.decode("utf-8", errors="replace")
                        except Exception:
                            content = "(二进制内容)"
                    if content is None:
                        content = ""

                    msg_type_label = {
                        1: "text",
                        3: "image",
                        34: "voice",
                        42: "card",
                        43: "video",
                        47: "emoji",
                        48: "location",
                        49: "link",
                        50: "call",
                        10000: "system",
                        10002: "recall",
                    }.get(local_type, f"type_{local_type}")

                    dt = datetime.fromtimestamp(create_time, tz=CN_TZ)
                    messages.append(
                        {
                            "time": dt.strftime("%Y-%m-%d %H:%M:%S"),
                            "timestamp": create_time,
                            "sender": sender,
                            "is_me": is_me,
                            "content": content,
                            "msg_type": msg_type_label,
                            "weekday": dt.weekday(),
                            "hour": dt.hour,
                        }
                    )
            except Exception as e:
                logger.warning("查询 %s 失败: %s", db_path, e)
            finally:
                conn.close()

        messages.sort(key=lambda m: m["timestamp"])
        return messages


def filter_text_only(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [m for m in messages if m["msg_type"] == "text"]
