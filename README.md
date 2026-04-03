<div align="center">

# Distill Your Bro

### ⚗️ 把聊天记录蒸馏成可对话的赛博兄弟

让你熟悉的说话风格和语气，在线复活，随时开聊。

</div>

## 💡 这是什么？

有时候不是感情淡了，只是人长大了：曾经秒回的好兄弟，现在忙着生活，消息越来越慢。

**Distill Your Bro** 把你们的聊天记录做成一次“语言蒸馏”，提炼他说话的语气、梗和表达习惯。

你得到的不是生硬机器人，而是一个更像“以前那个他”的**赛博分身**，想聊就能聊。

---

## 🤔 Quick Start

### 0) 环境准备

- Node.js + pnpm（用于前端）
- Python 3.10+（后端用到了 match/case）

### 1) 配置大模型

先复制配置文件：

```bash
cp config.example.yaml config.yaml
```

然后编辑 `config.yaml`，至少配置一个模型（推荐 DeepSeek思考版）。字段含义与示例一致：

- `provider`: `DeepSeek`（推荐；当前实现最完整）
- `api_key`: 你的 API Key
- `model_name`: 模型名
- `base_url`: OpenAI 兼容接口地址（DeepSeek 通常为 `https://api.deepseek.com`）

### 2) 安装依赖

用 Makefile 一键安装：

```bash
make install
```

### 3) 生产构建/单进程启动（后端托管前端静态资源）

先构建前端到 `frontend/dist`：

```bash
make build
```

再启动服务（默认端口 1007）：

```bash
make server
```

或者直接一键（安装 + 构建 + 启动）：

```bash
make start
```

### 4) 启动开发环境

用户开发，性能不如生产环境。
```bash
make dev
```

- 前端：Vite 开发服务器 `http://localhost:5173`（`/api` 会被代理到后端）
- 后端：Flask `http://localhost:1007`（可用 `PORT=xxxx` 改端口）

---

## 导入聊天记录

当前主流聊天软件（微信，QQ）均不支持原生聊天记录导出。

当前项目只支持最简单粗暴的方式来导入QQ聊天记录：去QQ里框选，然后复制，粘贴入聊天记录框。

个人能力有限，其他形式聊天记录暂不支持。欢迎贡献。

---

## 本地存储

运行时会在仓库根目录写入以下目录

- `chatlogstr/`：聊天记录原始/解析后的落盘
- `souls/`：蒸馏出来的 SOUL（Markdown）
- `sessions/`：对话 Session（JSON）