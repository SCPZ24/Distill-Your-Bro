"""
聊天记录导入：抽象基类与微信实现。

微信数据来源（实现位于同目录 wechat/ 包，自包含）：
  1. 使用 wechat-decrypt 等工具解密 PC 微信本地库，得到含 message/ 与 contact/ 的目录；
  2. 传入该目录（或项目根目录下含 decrypted/）；
  3. 通过联系人表解析好友 wxid，在 message_*.db 中按 Msg_<md5(wxid)> 表读取消息。

QQ 导出将在后续单独实现派生类。
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from .wechat.session_loader import load_wechat_chat_data


class ChatLogLoader(ABC):
    """聊天记录加载器基类。子类负责平台相关解析，统一产出可序列化结构供 LLM 使用。"""

    @abstractmethod
    def load_chat_log(self) -> Dict[str, Any]:
        """加载并返回结构化聊天记录（JSON 可序列化 dict）。"""
        raise NotImplementedError


class WechatChatLogLoader(ChatLogLoader):
    """
    从解密后的微信 SQLite 目录加载与指定好友的单聊记录。

    :param decrypted_root: 解密库根目录（直接含 message/、contact/），或
        上层目录（其下含 decrypted/）。
    :param friend: 好友备注、昵称、微信号或 wxid。
    :param my_name: 在对话中代表自己的发送者显示名（默认「我」）。
    :param text_only: True 时只导出文本消息，更适合直接拼进 prompt。
    """

    def __init__(
        self,
        decrypted_root: str,
        friend: str,
        *,
        my_name: str = "我",
        text_only: bool = True,
    ) -> None:
        self._decrypted_root = os.path.abspath(decrypted_root)
        self._friend = friend
        self._my_name = my_name
        self._text_only = text_only

    def load_chat_log(self) -> Dict[str, Any]:
        raw = load_wechat_chat_data(
            self._decrypted_root,
            self._friend,
            self._my_name,
        )
        messages: List[Dict[str, Any]] = (
            list(raw["text_messages"])
            if self._text_only
            else list(raw["all_messages"])
        )
        return {
            "platform": "wechat",
            "meta": {
                "wxid": raw["wxid"],
                "friend_name": raw["friend_name"],
                "my_name": raw["my_name"],
                "db_dir": raw["db_dir"],
                "total_count": raw["total_count"],
                "text_count": raw["text_count"],
                "text_only": self._text_only,
            },
            "messages": _messages_for_prompt(messages),
        }


def _messages_for_prompt(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """保留 LLM 蒸馏所需字段，去掉 weekday/hour 等可选统计字段。"""
    out: List[Dict[str, Any]] = []
    for m in messages:
        out.append(
            {
                "time": m.get("time"),
                "timestamp": m.get("timestamp"),
                "sender": m.get("sender"),
                "is_me": m.get("is_me"),
                "content": m.get("content"),
                "msg_type": m.get("msg_type"),
            }
        )
    return out
