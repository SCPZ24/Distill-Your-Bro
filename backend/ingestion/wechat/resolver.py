"""将备注/昵称/微信号/wxid 解析为好友 wxid。"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class WechatFriendResolver:
    """
    支持: wxid 直接匹配、备注、昵称、微信号(alias/wechat_id)、模糊匹配。
    多人匹配时返回 None（由上层抛错提示用户收紧条件）。
    """

    def resolve(self, contacts: Dict[str, Dict[str, Any]], friend_input: str) -> Optional[str]:
        friend_input = friend_input.strip("\"'")

        if friend_input in contacts:
            return friend_input

        if friend_input.startswith("wxid_"):
            for wxid in contacts:
                if wxid == friend_input:
                    return friend_input
            return friend_input

        lower_input = friend_input.lower()

        exact_matches: List[Tuple[str, str]] = []
        for wxid, info in contacts.items():
            if lower_input == info["remark"].lower():
                exact_matches.append((wxid, "备注名"))
            elif lower_input == info["nick_name"].lower():
                exact_matches.append((wxid, "昵称"))
            elif "alias" in info and lower_input == info["alias"].lower():
                exact_matches.append((wxid, "微信号"))
            elif "wechat_id" in info and lower_input == info["wechat_id"].lower():
                exact_matches.append((wxid, "微信号"))

        if exact_matches:
            wxid, match_type = exact_matches[0]
            logger.info("好友精确匹配: %s (%s: %s)", wxid, match_type, friend_input)
            return wxid

        candidates: List[Tuple[str, str]] = []
        for wxid, info in contacts.items():
            if lower_input in info["remark"].lower():
                candidates.append((wxid, f"备注名包含 '{friend_input}'"))
            elif lower_input in info["nick_name"].lower():
                candidates.append((wxid, f"昵称包含 '{friend_input}'"))
            elif "alias" in info and lower_input in info["alias"].lower():
                candidates.append((wxid, f"微信号包含 '{friend_input}'"))
            elif "wechat_id" in info and lower_input in info["wechat_id"].lower():
                candidates.append((wxid, f"微信号包含 '{friend_input}'"))
            elif lower_input in wxid.lower():
                candidates.append((wxid, f"wxid 包含 '{friend_input}'"))

        if len(candidates) == 1:
            wxid, reason = candidates[0]
            logger.info("好友模糊匹配: %s (%s)", wxid, reason)
            return wxid
        if len(candidates) > 1:
            logger.info("好友匹配不唯一，共 %s 个候选", len(candidates))
            for wxid, reason in candidates[:10]:
                info = contacts[wxid]
                logger.info(
                    "  - %s (%s, 昵称: %s, 备注: %s)",
                    wxid,
                    reason,
                    info["nick_name"],
                    info["remark"],
                )
            return None

        logger.info("未在联系人表中找到匹配，将 '%s' 当作 wxid 使用", friend_input)
        return friend_input
