from backend.models.model import Model
from typing import Optional
from openai import OpenAI

class DeepSeekModel(Model):
    def __init__(self, config: dict):
        try:
            self.name = config["name"]
            self.api_key = config["api_key"]
            self.model_name = config["model_name"]
            self.base_url = config["base_url"]
        except KeyError as e:
            raise ValueError(f"DeepSeek 配置缺少字段: {e.args[0]}") from e
    
    def generate(self, prompt: str) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt 不能为空")

        base_url = self.base_url.strip().strip("`").strip()
        candidates = [base_url]
        if "/v1" not in base_url.rstrip("/"):
            candidates.append(base_url.rstrip("/") + "/v1")

        last_error: Optional[Exception] = None
        for url in candidates:
            try:
                client = OpenAI(api_key=self.api_key, base_url=url)
                resp = client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    stream=False,
                )
                msg = resp.choices[0].message
                content = getattr(msg, "content", None)
                if isinstance(content, str) and content.strip():
                    return content
                reasoning = getattr(msg, "reasoning_content", None)
                if isinstance(reasoning, str) and reasoning.strip():
                    return reasoning
                return str(content or reasoning or "")
            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(f"DeepSeek 调用失败: {last_error}") from last_error
