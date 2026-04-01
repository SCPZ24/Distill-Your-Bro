"""组合路径、联系人、好友解析与消息表，产出与参考实现一致的会话数据包。"""

from __future__ import annotations

import logging
from typing import Any, Dict

from .contacts import WechatContactRepository
from .messages import WechatMessageRepository, filter_text_only
from .paths import WechatDecryptedPath
from .resolver import WechatFriendResolver

logger = logging.getLogger(__name__)


class WechatSessionLoader:
    """
    从解密目录加载与指定好友的会话（单聊）。

    等价于原 wechat-chat-analyzer 中 load_chat_data 的流程，便于单测与复用。
    """

    def __init__(
        self,
        decrypted_search_path: str,
        friend: str,
        my_name: str = "我",
    ) -> None:
        self._decrypted_search_path = decrypted_search_path
        self._friend = friend
        self._my_name = my_name

    def load(self) -> Dict[str, Any]:
        return load_wechat_chat_data(
            self._decrypted_search_path,
            self._friend,
            self._my_name,
        )


def load_wechat_chat_data(db_dir: str, friend: str, my_name: str = "我") -> Dict[str, Any]:
    """
    返回:
      db_dir, wxid, friend_name, my_name, contacts,
      all_messages, text_messages, total_count, text_count
    """
    db_dir = WechatDecryptedPath.resolve(db_dir)
    logger.info("使用数据库目录: %s", db_dir)

    contacts = WechatContactRepository().load(db_dir)
    logger.info("加载了 %s 个联系人", len(contacts))
    if not contacts:
        logger.warning("未加载到任何联系人，可能是 contact.db 不存在或损坏")

    wxid = WechatFriendResolver().resolve(contacts, friend)
    if not wxid:
        raise ValueError(f"无法匹配好友: '{friend}'")

    friend_info = contacts.get(wxid, {})
    friend_name = friend_info.get("display_name", wxid)
    logger.info("目标好友: %s (%s)", friend_name, wxid)

    all_messages = WechatMessageRepository(db_dir).extract_thread(
        wxid, my_name=my_name, friend_display=friend_name
    )
    text_messages = filter_text_only(all_messages)
    logger.info(
        "共提取 %s 条消息 (其中文本 %s 条)",
        len(all_messages),
        len(text_messages),
    )
    if not all_messages:
        logger.warning("未提取到任何消息")

    return {
        "db_dir": db_dir,
        "wxid": wxid,
        "friend_name": friend_name,
        "my_name": my_name,
        "contacts": contacts,
        "all_messages": all_messages,
        "text_messages": text_messages,
        "total_count": len(all_messages),
        "text_count": len(text_messages),
    }
