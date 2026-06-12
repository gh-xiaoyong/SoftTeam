"""贪吃蛇 Demo 执行入口。

阶段 4D 使用真实 CrewAI 链路执行 4 个任务，并把结构化中间产物保存到磁盘。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from config import get_llm_settings, is_llm_configured
from schemas import ArchitecturePlan, CodeManifest, RequirementDocument, TestReport
from tools.artifact_writer import (
    save_architecture_plan,
    save_code_manifest,
    save_requirement_document,
    save_test_report,
)
from tools.test_runner import run_predefined_test_cases
from workflow.sequential_crew import build_sequential_crew


SNAKE_GAME_REQUEST = (
    "实现一个贪吃蛇 HTML 游戏。要求使用纯 HTML、CSS、JavaScript，"
    "支持方向键控制蛇移动，显示分数，吃到食物后蛇变长并加分，"
    "撞墙或撞到自己后游戏结束，并提供重新开始按钮。"
)


def ensure_llm_configured() -> None:
    """检查运行 CrewAI Demo 所需的基础模型配置。"""

    if not is_llm_configured():
        raise RuntimeError(
            "未检测到可用的模型密钥。请先在环境变量或 .env 文件中配置 "
            "DEEPSEEK_API_KEY 或 OPENAI_API_KEY，"
            "然后再运行 `.venv\\Scripts\\python.exe main.py --run-demo`。"
        )

    settings = get_llm_settings()
    if not settings.model:
        raise RuntimeError("未检测到模型名称，请配置 DEEPSEEK_MODEL 或 OPENAI_MODEL_NAME。")


def _get_task_model(task_output: object, expected_type: type[BaseModel]) -> BaseModel:
    """从 CrewAI 任务输出中取出指定类型的 Pydantic 结果。"""

    model = getattr(task_output, "pydantic", None)
    if isinstance(model, expected_type):
        return model

    raw = getattr(task_output, "raw", "")
    if not raw:
        raise TypeError(f"任务输出缺少 raw 内容，无法解析为 {expected_type.__name__}。")

    json_text = _extract_json_object(raw)
    data = json.loads(json_text)
    normalized_data = _normalize_model_data(data, expected_type)
    return expected_type.model_validate(normalized_data)


def _extract_json_object(text: str) -> str:
    """从模型原始输出中提取 JSON 对象文本。"""

    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("模型输出中没有找到合法 JSON 对象。")

    return cleaned[start : end + 1]


def _normalize_model_data(data: Any, expected_type: type[BaseModel]) -> Any:
    """把模型输出的近似 JSON 规范化为本项目 Schema 需要的结构。"""

    if expected_type is RequirementDocument and isinstance(data, dict):
        return _normalize_requirement_document(data)

    if expected_type is ArchitecturePlan and isinstance(data, dict):
        return _normalize_architecture_plan(data)

    if expected_type is CodeManifest and isinstance(data, dict):
        return _normalize_code_manifest(data)

    if expected_type is TestReport and isinstance(data, dict):
        return _normalize_test_report(data)

    return data


def _as_list(value: Any) -> list[Any]:
    """把单个值规范化为列表。"""

    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _stringify(value: Any) -> str:
    """把模型输出值稳定转成字符串。"""

    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def _normalize_requirement_document(data: dict[str, Any]) -> dict[str, Any]:
    """兼容需求文档中常见的字符串简写。"""

    normalized = dict(data)
    normalized["target_users"] = [_stringify(item) for item in _as_list(data.get("target_users"))]
    normalized["features"] = [
        _normalize_feature_requirement(item) for item in _as_list(data.get("features"))
    ]
    normalized["user_interactions"] = [
        _normalize_user_interaction(item) for item in _as_list(data.get("user_interactions"))
    ]
    normalized["acceptance_criteria"] = [
        _normalize_acceptance_criterion(item)
        for item in _as_list(data.get("acceptance_criteria"))
    ]
    return normalized


def _normalize_feature_requirement(value: Any) -> dict[str, str]:
    """把功能点字符串或简写对象规范化为 FeatureRequirement。"""

    if isinstance(value, dict):
        return {
            "name": _stringify(value.get("name") or value.get("title") or value.get("feature")),
            "description": _stringify(
                value.get("description") or value.get("detail") or value.get("summary") or value
            ),
            "priority": _stringify(value.get("priority") or "medium"),
        }

    text = _stringify(value)
    return {
        "name": text,
        "description": text,
        "priority": "medium",
    }


def _normalize_user_interaction(value: Any) -> dict[str, str]:
    """把交互字符串或简写对象规范化为 UserInteraction。"""

    if isinstance(value, dict):
        return {
            "action": _stringify(value.get("action") or value.get("user_action") or value),
            "expected_result": _stringify(
                value.get("expected_result")
                or value.get("result")
                or value.get("expected")
                or value
            ),
        }

    text = _stringify(value)
    return {
        "action": text,
        "expected_result": text,
    }


def _normalize_acceptance_criterion(value: Any) -> dict[str, str]:
    """把验收标准字符串或简写对象规范化为 AcceptanceCriterion。"""

    if isinstance(value, dict):
        return {
            "criterion": _stringify(
                value.get("criterion") or value.get("description") or value.get("text") or value
            )
        }

    return {"criterion": _stringify(value)}


def _normalize_architecture_plan(data: dict[str, Any]) -> dict[str, Any]:
    """兼容架构方案中常见的字符串简写。"""

    normalized = dict(data)
    normalized["tech_stack"] = [_stringify(item) for item in _as_list(data.get("tech_stack"))]
    normalized["files"] = [_normalize_file_design(item) for item in _as_list(data.get("files"))]
    normalized["modules"] = [
        _normalize_module_design(item) for item in _as_list(data.get("modules"))
    ]
    normalized["data_flow"] = [_stringify(item) for item in _as_list(data.get("data_flow"))]
    normalized["implementation_notes"] = [
        _stringify(item) for item in _as_list(data.get("implementation_notes"))
    ]
    return normalized


def _normalize_file_design(value: Any) -> dict[str, str]:
    """把文件设计简写规范化为 FileDesign。"""

    if isinstance(value, dict):
        path = _stringify(value.get("path") or value.get("file") or value.get("name"))
        return {
            "path": path,
            "responsibility": _stringify(
                value.get("responsibility") or value.get("purpose") or value.get("description") or path
            ),
        }

    text = _stringify(value)
    return {"path": text, "responsibility": text}


def _normalize_module_design(value: Any) -> dict[str, Any]:
    """把模块设计简写规范化为 ModuleDesign。"""

    if isinstance(value, dict):
        name = _stringify(value.get("name") or value.get("module") or value.get("title"))
        return {
            "name": name,
            "responsibility": _stringify(
                value.get("responsibility") or value.get("description") or value.get("purpose") or name
            ),
            "dependencies": [
                _stringify(item) for item in _as_list(value.get("dependencies"))
            ],
        }

    text = _stringify(value)
    return {"name": text, "responsibility": text, "dependencies": []}


def _normalize_code_manifest(data: dict[str, Any]) -> dict[str, Any]:
    """兼容代码清单中常见的文件字段别名。"""

    normalized = dict(data)
    normalized["files"] = [
        _normalize_generated_file(item) for item in _as_list(data.get("files"))
    ]
    return normalized


def _normalize_generated_file(value: Any) -> dict[str, str]:
    """把生成文件简写规范化为 GeneratedFile。"""

    if isinstance(value, dict):
        path = _stringify(value.get("path") or value.get("file") or value.get("name"))
        return {
            "path": path,
            "purpose": _stringify(value.get("purpose") or value.get("description") or path),
            "language": _stringify(value.get("language") or value.get("type") or _guess_language(path)),
            "content": _stringify(value.get("content") or value.get("source") or value.get("code")),
        }

    text = _stringify(value)
    return {
        "path": text,
        "purpose": text,
        "language": _guess_language(text),
        "content": "",
    }


def _guess_language(path: str) -> str:
    """根据文件后缀推断语言。"""

    suffix = Path(path).suffix.lower()
    return {
        ".html": "html",
        ".css": "css",
        ".js": "javascript",
        ".json": "json",
        ".md": "markdown",
    }.get(suffix, "text")


def _normalize_test_report(data: dict[str, Any]) -> dict[str, Any]:
    """兼容测试报告中常见的字符串简写。"""

    normalized = dict(data)
    normalized["cases"] = [_normalize_test_case(item) for item in _as_list(data.get("cases"))]
    normalized["defects"] = [
        _normalize_defect_report(item) for item in _as_list(data.get("defects"))
    ]
    normalized["total"] = _to_int(data.get("total"), len(normalized["cases"]))
    normalized["passed_count"] = _to_int(
        data.get("passed_count"),
        sum(1 for item in normalized["cases"] if item["passed"]),
    )
    normalized["failed_count"] = _to_int(
        data.get("failed_count"),
        normalized["total"] - normalized["passed_count"],
    )
    normalized["passed"] = _normalize_report_passed(data.get("passed"), normalized)
    return normalized


def _normalize_test_case(value: Any) -> dict[str, Any]:
    """把测试用例简写规范化为 TestCaseResult。"""

    if isinstance(value, dict):
        name = _stringify(value.get("name") or value.get("case") or value.get("title"))
        return {
            "name": name,
            "passed": _to_bool(value.get("passed"), default=False),
            "expected": _stringify(value.get("expected") or ""),
            "actual": _stringify(value.get("actual") or ""),
            "detail": _stringify(value.get("detail") or value.get("description") or ""),
        }

    text = _stringify(value)
    return {
        "name": text,
        "passed": False,
        "expected": "",
        "actual": text,
        "detail": text,
    }


def _normalize_defect_report(value: Any) -> dict[str, str]:
    """把缺陷简写规范化为 DefectReport。"""

    if isinstance(value, dict):
        case_name = _stringify(value.get("case_name") or value.get("case") or value.get("name"))
        return {
            "case_name": case_name,
            "severity": _stringify(value.get("severity") or "medium"),
            "description": _stringify(value.get("description") or value.get("detail") or case_name),
            "suggestion": _stringify(value.get("suggestion") or value.get("fix") or ""),
        }

    text = _stringify(value)
    return {
        "case_name": text,
        "severity": "medium",
        "description": text,
        "suggestion": "",
    }


def _to_int(value: Any, default: int = 0) -> int:
    """把模型输出值转换成整数。"""

    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return default
    return default


def _to_bool(value: Any, default: bool = False) -> bool:
    """把模型输出值转换成布尔值。"""

    if isinstance(value, bool):
        return value
    if isinstance(value, int | float):
        if value == 1:
            return True
        if value == 0:
            return False
        return default
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "y", "1", "pass", "passed", "通过", "是"}:
            return True
        if lowered in {"false", "no", "n", "0", "fail", "failed", "失败", "否"}:
            return False
    return default


def _normalize_report_passed(value: Any, report: dict[str, Any]) -> bool:
    """规范化测试报告的整体 passed 字段。"""

    direct = _to_bool(value, default=False)
    if isinstance(value, bool):
        return direct
    if isinstance(value, str) and value.strip().lower() in {
        "true",
        "yes",
        "y",
        "1",
        "pass",
        "passed",
        "通过",
        "是",
        "false",
        "no",
        "n",
        "0",
        "fail",
        "failed",
        "失败",
        "否",
    }:
        return direct

    return report["failed_count"] == 0 and report["passed_count"] == report["total"]


def run_snake_demo() -> list[Path]:
    """执行贪吃蛇 Demo，并使用本地 Test Runner 生成最终测试报告。"""

    ensure_llm_configured()

    build_result = build_sequential_crew(SNAKE_GAME_REQUEST)
    build_result.crew.kickoff()

    requirement = _get_task_model(
        build_result.tasks["requirement"].output,
        RequirementDocument,
    )
    architecture = _get_task_model(
        build_result.tasks["architecture"].output,
        ArchitecturePlan,
    )
    code_manifest = _get_task_model(
        build_result.tasks["development"].output,
        CodeManifest,
    )

    written_files: list[Path] = []
    written_files.extend(save_requirement_document(requirement))
    written_files.extend(save_architecture_plan(architecture))
    written_files.extend(save_code_manifest(code_manifest))

    test_report = run_predefined_test_cases(code_manifest.project_root)
    written_files.extend(save_test_report(test_report))

    return written_files
