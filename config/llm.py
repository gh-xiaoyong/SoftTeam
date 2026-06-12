"""LLM 配置读取工具。

当前项目按 OpenAI-compatible 方式接入 DeepSeek。
配置来源优先读取 `.env`，也支持系统环境变量。
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from crewai import LLM
from dotenv import load_dotenv


PLACEHOLDER_VALUES = {
    "",
    "请替换为你的DeepSeek_API_Key",
    "sk-xxxxxxxxxxxxxxxxxxxxxxxx",
    "your_api_key",
    "your-deepseek-api-key",
}


@dataclass(frozen=True)
class LLMSettings:
    """运行 Agent 时需要的模型配置。"""

    api_key: str
    base_url: str
    model: str


def get_llm_settings() -> LLMSettings:
    """从环境变量读取 LLM 配置。"""

    load_dotenv()

    api_key = (
        os.getenv("DEEPSEEK_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or os.getenv("LLM_API_KEY")
        or ""
    )
    base_url = (
        os.getenv("DEEPSEEK_BASE_URL")
        or os.getenv("OPENAI_API_BASE")
        or os.getenv("OPENAI_BASE_URL")
        or os.getenv("LLM_BASE_URL")
        or "https://api.deepseek.com"
    )
    model = (
        os.getenv("DEEPSEEK_MODEL")
        or os.getenv("OPENAI_MODEL_NAME")
        or os.getenv("LLM_MODEL")
        or "deepseek-v4-flash"
    )

    return LLMSettings(
        api_key=api_key.strip(),
        base_url=base_url.strip(),
        model=model.strip(),
    )


def is_llm_configured() -> bool:
    """判断是否已经配置了可用的模型密钥。"""

    settings = get_llm_settings()
    return settings.api_key not in PLACEHOLDER_VALUES


def supports_native_response_format() -> bool:
    """判断当前模型是否适合使用原生结构化输出。

    DeepSeek 当前 OpenAI-compatible 接口不适合使用 CrewAI 的
    `output_pydantic` 原生 response_format 路径，所以这里默认关闭。
    """

    settings = get_llm_settings()
    model = settings.model.lower()
    base_url = settings.base_url.lower()
    return "deepseek" not in model and "deepseek" not in base_url


def create_configured_llm() -> LLM | None:
    """创建 CrewAI 使用的 LLM 对象。

    如果还没有配置真实密钥，返回 `None`。
    这样默认查看编排计划时不会因为缺少密钥而失败。
    """

    if not is_llm_configured():
        return None

    settings = get_llm_settings()
    return LLM(
        model=settings.model,
        api_key=settings.api_key,
        base_url=settings.base_url,
        provider="openai",
        temperature=0.2,
    )
