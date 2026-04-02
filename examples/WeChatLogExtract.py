#!/usr/bin/env python3
"""
微信聊天记录导出示例（供 LLM prompt 或下游蒸馏使用）

前置条件
--------
1. 使用 wechat-decrypt 等工具解密 PC 微信本地库，得到目录结构：
   - contact/contact.db
   - message/message_*.db
2. 将解密根目录路径传给 --db-dir（也可传上层目录，若其下存在 decrypted/ 子目录）。

用法
----
在项目仓库根目录执行::

    PYTHONPATH=backend python examples/WeChatLogExtract.py \\
        --db-dir /path/to/decrypted \\
        --friend \"好友备注或昵称或wxid\"

或直接运行（脚本会自动把 backend 加入模块搜索路径）::

    python examples/WeChatLogExtract.py --db-dir ... --friend ...

输出为 JSON：platform、meta（条数与路径等）、messages（默认仅文本行）。

代码中也可这样调用::

    from ingestion import WechatChatLogLoader

    loader = WechatChatLogLoader(\"/path/to/decrypted\", \"好友名\", my_name=\"我\", text_only=True)
    data = loader.load_chat_log()  # dict，可 json.dumps
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _ensure_backend_on_path() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    backend = repo_root / "backend"
    if str(backend) not in sys.path:
        sys.path.insert(0, str(backend))


def main() -> int:
    _ensure_backend_on_path()
    from ingestion import WechatChatLogLoader

    parser = argparse.ArgumentParser(
        description="从解密后的微信 SQLite 导出与指定好友的单聊（JSON）。"
    )
    parser.add_argument(
        "--db-dir",
        required=True,
        help="解密库根目录（含 message/ 与 contact/），或含 decrypted/ 的上级路径",
    )
    parser.add_argument(
        "--friend",
        required=True,
        help="好友备注名、昵称、微信号或 wxid（需能唯一匹配）",
    )
    parser.add_argument(
        "--my-name",
        default="我",
        help="自己在对话中的显示名（默认：我）",
    )
    parser.add_argument(
        "--all-message-types",
        action="store_true",
        help="包含图片/语音等非文本消息（默认仅导出文本，更适合拼 prompt）",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="写入 JSON 文件路径；省略则打印到标准输出",
    )
    args = parser.parse_args()

    loader = WechatChatLogLoader(
        args.db_dir,
        args.friend,
        my_name=args.my_name,
        text_only=not args.all_message_types,
    )
    data = loader.load_chat_log()

    text = json.dumps(data, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"已写入: {args.output}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
