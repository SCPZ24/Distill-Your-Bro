# 后端接口文档（MVP）

## 全局约定

### Base URL

`/api`

### Content-Type

- 请求：`application/json; charset=utf-8`
- 响应：`application/json; charset=utf-8`

### 通用响应格式

成功：

```json
{
  "ok": true,
  "data": {}
}
```

失败：

```json
{
  "ok": false,
  "error": {
    "code": "STRING_CODE",
    "message": "人类可读的错误信息"
  }
}
```

### 错误码（建议）

- `INVALID_ARGUMENT`：参数格式错误/缺失
- `NOT_FOUND`：资源不存在（SOUL、Session、文件等）
- `LLM_ERROR`：大模型调用失败
- `IO_ERROR`：文件读写失败

### 存储约定（与 PRD 一致）

- SOUL 文件：仓库根目录 `souls/` 下，文件名 `{bro_name}_SOUL.md`
- Session 文件：仓库根目录 `sessions/` 下，文件名 `{session_id}.json`

## SOUL（人格）相关接口

### 1) 解析聊天记录（生成可用于蒸馏的字符串）

前端可能上传不同来源的聊天记录；MVP 可以先支持“直接上传结构化 JSON 或纯文本”，后续再扩展更多格式。

`POST /api/chatlogs/parse`

请求：

```json
{
  "platform": "wechat",
  "payload": "原始聊天记录（纯文本等）",
  "options": {
    "text_only": true,
    "my_name": "我"
  }
}
```

响应：

```json
{
  "ok": true,
  "data": {}
}
```
注意虽然这里没有相应，但是系统会自己把解析后的聊天记录存储起来，后续用于蒸馏。
存储在目录/chatlogstr/。
存储的文件名{bro_name}.txt，内容就为解析后的聊天记录字符串。

### 2) 发起蒸馏（生成 SOUL）

`POST /api/souls/distill`

请求：

```json
{
  "bro_name": "张三",
}
```

响应：

```json
{
  "ok": true,
  "data": {
    "bro_name": "张三",
    "soul_markdown": "# 角色：..."
  }
}
```

说明：

- 该接口只负责“生成”，是否保存由前端下一步确认后调用保存接口。

### 3) 保存 SOUL（写入 /souls）

`POST /api/souls/save`

请求：

```json
{
  "bro_name": "张三",
  "soul_markdown": "# 角色：..."
}
```

响应：

```json
{
  "ok": true,
  "data": {
    "path": "souls/张三_SOUL.md"
  }
}
```

### 4) 列出 SOUL

`GET /api/souls`

响应：

```json
{
  "ok": true,
  "data": {
    "souls": [
      {
        "bro_name": "张三",
        "file_name": "张三_SOUL.md"
      }
    ]
  }
}
```

### 5) 获取/导出 SOUL（Markdown）

`GET /api/souls/{bro_name}`

响应：

```json
{
  "ok": true,
  "data": {
    "bro_name": "张三",
    "soul_markdown": "# 角色：..."
  }
}
```

### 6) 删除 SOUL

`DELETE /api/souls/{bro_name}`

响应：

```json
{
  "ok": true,
  "data": {
    "deleted": true
  }
}
```

## Session（对话）相关接口

Session 用于管理用户与 bro 的对话上下文；PRD 要求将对话历史保存到 `sessions/` 目录下 JSON 文件。

### Session JSON 格式（建议）

```json
{
  "session_id": "uuid-or-slug",
  "bro_name": "张三",
  "chat_history": [
    {
      "user_msg": "在干嘛？",
      "bro_msg": "..."
    }
  ]
}
```

### 1) 创建/打开 Session

`POST /api/sessions`

请求：

```json
{
  "session_id": "可选：前端传入；不传则后端生成"
}
```

响应：

```json
{
  "ok": true,
  "data": {
    "session_id": "xxx",
    "bro_name": "张三",
    "chat_history": []
  }
}
```

### 2) 列出 Session

`GET /api/sessions`

响应：

```json
{
  "ok": true,
  "data": {
    "sessions": [
      {
        "session_id": "xxx",
        "bro_name": "张三"
      }
    ]
  }
}
```

### 3) 获取 Session 详情（含历史）

`GET /api/sessions/{session_id}`

响应：

```json
{
  "ok": true,
  "data": {
    "session_id": "xxx",
    "bro_name": "张三",
    "chat_history": [
      {
        "user_msg": "在干嘛？",
        "bro_msg": "..."
      }
    ]
  }
}
```

### 4) 发送消息（生成回复并追加历史）

`POST /api/sessions/{session_id}/messages`

请求：

```json
{
  "user_msg": "在干嘛？"
}
```

响应：

```json
{
  "ok": true,
  "data": {
    "bro_msg": "..."
  }
}
```

说明：

- 后端需要读取对应 bro 的 `souls/{bro_name}_SOUL.md` 作为 system prompt，并拼接 session history 形成最终 prompt，调用 LLM 生成回复。
- 成功后将本轮 `{user_msg, bro_msg}` 追加写回 `sessions/{session_id}.json`。

### 5) 删除 Session

`DELETE /api/sessions/{session_id}`

响应：

```json
{
  "ok": true,
  "data": {
    "deleted": true
  }
}
```