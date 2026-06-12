"""项目文件读写工具。

后续 Agent 不直接操作 `open()` 或路径拼接，而是通过这里的函数写入产物。
这样可以把路径规范、目录创建、编码格式等细节集中管理。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def resolve_project_path(relative_path: str | Path) -> Path:
    """把项目内相对路径解析成绝对路径。

    本项目的生成文件都应该写在项目目录下，所以这里拒绝绝对路径。
    这样可以避免 Agent 产物意外写到项目外部。
    """

    path = Path(relative_path)
    if path.is_absolute():
        raise ValueError(f"只允许传入项目内相对路径，不允许绝对路径：{path}")

    return (PROJECT_ROOT / path).resolve()


def ensure_parent_dir(file_path: str | Path) -> Path:
    """确保目标文件的父目录存在，并返回目标绝对路径。"""

    resolved_path = resolve_project_path(file_path)
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    return resolved_path


def write_text_file(file_path: str | Path, content: str) -> Path:
    """写入 UTF-8 文本文件。"""

    resolved_path = ensure_parent_dir(file_path)
    resolved_path.write_text(content, encoding="utf-8")
    return resolved_path


def read_text_file(file_path: str | Path) -> str:
    """读取 UTF-8 文本文件。"""

    resolved_path = resolve_project_path(file_path)
    return resolved_path.read_text(encoding="utf-8")


def write_json_file(file_path: str | Path, data: dict[str, Any] | list[Any]) -> Path:
    """写入格式化 JSON 文件。

    `ensure_ascii=False` 可以保留中文，不会把中文转成 Unicode 转义。
    """

    content = json.dumps(data, ensure_ascii=False, indent=2)
    return write_text_file(file_path, content + "\n")


def read_json_file(file_path: str | Path) -> Any:
    """读取 JSON 文件并解析成 Python 对象。"""

    content = read_text_file(file_path)
    return json.loads(content)


def write_model_json_file(file_path: str | Path, model: BaseModel) -> Path:
    """把 Pydantic 模型写入 JSON 文件。"""

    return write_json_file(file_path, model.model_dump())


def list_project_files(directory: str | Path) -> list[Path]:
    """列出项目内某个目录下的全部文件。"""

    resolved_dir = resolve_project_path(directory)
    if not resolved_dir.exists():
        return []

    return sorted(path for path in resolved_dir.rglob("*") if path.is_file())

