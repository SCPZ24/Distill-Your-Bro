"""联系人 contact.db 读取。"""

from __future__ import annotations

import logging
import os
import sqlite3
from typing import Any, Dict

logger = logging.getLogger(__name__)

# 与微信 data_loader 一致: {wxid: {nick_name, remark, display_name, alias?/wechat_id?}}
ContactMap = Dict[str, Dict[str, Any]]


class WechatContactRepository:
    """从 contact/contact.db 加载联系人映射。"""

    def load(self, db_dir: str) -> ContactMap:
        contact_db = os.path.join(db_dir, "contact", "contact.db")
        if not os.path.exists(contact_db):
            logger.warning("联系人数据库不存在: %s", contact_db)
            return {}

        contacts: ContactMap = {}
        conn = sqlite3.connect(contact_db)
        try:
            cursor = conn.execute("PRAGMA table_info(contact)")
            columns = [row[1] for row in cursor.fetchall()]
            logger.debug("联系人表字段: %s", columns)

            if "alias" in columns:
                rows = conn.execute(
                    "SELECT username, nick_name, remark, alias FROM contact"
                ).fetchall()
                for username, nick_name, remark, alias in rows:
                    display = remark if remark else nick_name if nick_name else username
                    contacts[username] = {
                        "nick_name": nick_name or "",
                        "remark": remark or "",
                        "alias": alias or "",
                        "display_name": display,
                    }
            elif "wechat_id" in columns:
                rows = conn.execute(
                    "SELECT username, nick_name, remark, wechat_id FROM contact"
                ).fetchall()
                for username, nick_name, remark, wechat_id in rows:
                    display = remark if remark else nick_name if nick_name else username
                    contacts[username] = {
                        "nick_name": nick_name or "",
                        "remark": remark or "",
                        "wechat_id": wechat_id or "",
                        "display_name": display,
                    }
            else:
                rows = conn.execute(
                    "SELECT username, nick_name, remark FROM contact"
                ).fetchall()
                for username, nick_name, remark in rows:
                    display = remark if remark else nick_name if nick_name else username
                    contacts[username] = {
                        "nick_name": nick_name or "",
                        "remark": remark or "",
                        "display_name": display,
                    }
        except Exception as e:
            logger.warning("读取联系人数据库失败: %s", e)
        finally:
            conn.close()

        return contacts
