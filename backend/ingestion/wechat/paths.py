"""定位解密后的微信数据库根目录（含 message/ 与 contact/）。"""

from __future__ import annotations

import os


class WechatDecryptedPath:
    """在用户传入的路径上解析出真正的 decrypted 根目录。"""

    @staticmethod
    def resolve(search_path: str) -> str:
        """
        支持:
        - 直接传入 decrypted 目录（含 message/、contact/）
        - 传入 wechat-decrypt 等项目根目录（其下含 decrypted/）
        """
        search_path = os.path.abspath(search_path)
        if os.path.isdir(os.path.join(search_path, "message")) and os.path.isdir(
            os.path.join(search_path, "contact")
        ):
            return search_path

        decrypted = os.path.join(search_path, "decrypted")
        if os.path.isdir(decrypted) and os.path.isdir(os.path.join(decrypted, "message")):
            return decrypted

        raise FileNotFoundError(
            f"无法在 '{search_path}' 中找到解密后的数据库目录。\n"
            "请确保目录下包含 message/ 和 contact/ 子目录。\n"
            "如尚未解密，请先使用 wechat-decrypt 等工具解密微信数据库。"
        )
