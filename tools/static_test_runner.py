"""贪吃蛇页面静态测试器。

阶段 5A 只做静态测试，不启动浏览器，也不执行 JavaScript。
它检查生成目录中的 HTML/CSS/JS 文件和关键源码特征，并输出统一的 TestReport。
"""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

from schemas import DefectReport, TestCaseResult, TestReport
from tools.file_io import resolve_project_path


DEFAULT_SNAKE_PROJECT_ROOT = "generated/snake-game"


@dataclass(frozen=True)
class StaticCheckResult:
    """单条静态检查的中间结果。"""

    name: str
    passed: bool
    expected: str
    actual: str
    detail: str
    severity: str
    suggestion: str


class SnakeHtmlInspector(HTMLParser):
    """从 HTML 中提取测试需要的结构信息。"""

    def __init__(self) -> None:
        super().__init__()
        self.tags: set[str] = set()
        self.links: list[dict[str, str]] = []
        self.scripts: list[dict[str, str]] = []
        self.ids: set[str] = set()
        self.classes: set[str] = set()
        self.button_texts: list[str] = []
        self._button_depth = 0
        self._button_buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized_tag = tag.lower()
        attrs_dict = {
            name.lower(): value or ""
            for name, value in attrs
        }

        self.tags.add(normalized_tag)

        if "id" in attrs_dict:
            self.ids.add(attrs_dict["id"].lower())

        if "class" in attrs_dict:
            self.classes.update(
                class_name.lower()
                for class_name in attrs_dict["class"].split()
                if class_name.strip()
            )

        if normalized_tag == "link":
            self.links.append(attrs_dict)

        if normalized_tag == "script":
            self.scripts.append(attrs_dict)

        if normalized_tag == "button":
            self._button_depth += 1
            self._button_buffer = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "button" and self._button_depth > 0:
            text = "".join(self._button_buffer).strip().lower()
            if text:
                self.button_texts.append(text)
            self._button_depth -= 1
            self._button_buffer = []

    def handle_data(self, data: str) -> None:
        if self._button_depth > 0:
            self._button_buffer.append(data)


def run_static_snake_tests(project_root: str | Path = DEFAULT_SNAKE_PROJECT_ROOT) -> TestReport:
    """执行贪吃蛇项目的预定义静态测试，并返回结构化测试报告。"""

    root = resolve_project_path(project_root)
    index_path = root / "index.html"
    style_path = root / "style.css"
    script_path = root / "script.js"

    html = _read_optional_text(index_path)
    javascript = _read_optional_text(script_path)
    inspector = _inspect_html(html)

    checks = [
        _check_file_exists("index.html 文件存在", index_path),
        _check_file_exists("style.css 文件存在", style_path),
        _check_file_exists("script.js 文件存在", script_path),
        _check_html_references_assets(html, inspector),
        _check_game_area(html, inspector),
        _check_score_display(html, inspector),
        _check_restart_button(inspector),
        _check_direction_key_listener(javascript),
        _check_collision_logic(javascript),
        _check_scoring_logic(javascript),
    ]

    cases = [
        TestCaseResult(
            name=check.name,
            passed=check.passed,
            expected=check.expected,
            actual=check.actual,
            detail=check.detail,
        )
        for check in checks
    ]
    defects = [
        DefectReport(
            case_name=check.name,
            severity=check.severity,
            description=check.actual,
            suggestion=check.suggestion,
        )
        for check in checks
        if not check.passed
    ]

    passed_count = sum(1 for case in cases if case.passed)
    failed_count = len(cases) - passed_count
    passed = failed_count == 0

    return TestReport(
        passed=passed,
        total=len(cases),
        passed_count=passed_count,
        failed_count=failed_count,
        cases=cases,
        defects=defects,
        summary=_build_summary(project_root, passed, passed_count, failed_count),
    )


def _read_optional_text(path: Path) -> str:
    """读取文本文件；文件不存在时返回空字符串，便于继续生成完整报告。"""

    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _inspect_html(html: str) -> SnakeHtmlInspector:
    """解析 HTML；解析失败时保留空结果，让具体用例报告失败原因。"""

    inspector = SnakeHtmlInspector()
    if html:
        inspector.feed(html)
    return inspector


def _check_file_exists(name: str, file_path: Path) -> StaticCheckResult:
    exists = file_path.exists() and file_path.is_file()
    return StaticCheckResult(
        name=name,
        passed=exists,
        expected=f"生成目录中存在 {file_path.name}",
        actual="文件存在" if exists else f"未找到文件：{file_path}",
        detail="检查源码文件是否已落盘。",
        severity="high",
        suggestion=f"让开发 Agent 生成 {file_path.name}，并写入 generated/snake-game 目录。",
    )


def _check_html_references_assets(
    html: str,
    inspector: SnakeHtmlInspector,
) -> StaticCheckResult:
    has_css = any(
        "stylesheet" in link.get("rel", "").lower()
        and _is_same_file(link.get("href"), "style.css")
        for link in inspector.links
    )
    has_js = any(_is_same_file(script.get("src"), "script.js") for script in inspector.scripts)
    passed = has_css and has_js
    missing = []
    if not has_css:
        missing.append("style.css 引用")
    if not has_js:
        missing.append("script.js 引用")

    return StaticCheckResult(
        name="HTML 正确引用 CSS 和 JS",
        passed=passed,
        expected='index.html 包含 href="style.css" 和 src="script.js"',
        actual="引用完整" if passed else "缺少：" + "、".join(missing),
        detail="静态页面必须把样式和脚本接入入口 HTML。",
        severity="high",
        suggestion="在 index.html 的 head 中引用 style.css，并在 body 末尾引用 script.js。",
    )


def _check_game_area(html: str, inspector: SnakeHtmlInspector) -> StaticCheckResult:
    identifiers = inspector.ids | inspector.classes
    has_game_identifier = any(
        keyword in identifier
        for identifier in identifiers
        for keyword in ("game", "board", "grid", "canvas")
    )
    has_area = "canvas" in inspector.tags or has_game_identifier

    return StaticCheckResult(
        name="页面包含游戏区域",
        passed=has_area,
        expected="HTML 中存在 canvas，或存在可识别的 game/board/grid 游戏区域",
        actual="找到游戏区域" if has_area else "未找到 canvas 或游戏区域容器",
        detail=f"HTML 长度：{len(html)} 字符。",
        severity="high",
        suggestion='在 index.html 中添加 canvas，例如 <canvas id="game"></canvas>。',
    )


def _check_score_display(html: str, inspector: SnakeHtmlInspector) -> StaticCheckResult:
    identifiers = inspector.ids | inspector.classes
    has_score_identifier = any("score" in identifier for identifier in identifiers)
    has_score_text = "分数" in html or "score" in html.lower()
    passed = has_score_identifier or has_score_text

    return StaticCheckResult(
        name="页面包含分数显示",
        passed=passed,
        expected="HTML 中存在分数文本，或 id/class 包含 score 的元素",
        actual="找到分数显示" if passed else "未找到分数显示元素",
        detail="分数显示用于验证吃到食物后的计分反馈。",
        severity="medium",
        suggestion='添加分数元素，例如 <span id="score">0</span>。',
    )


def _check_restart_button(inspector: SnakeHtmlInspector) -> StaticCheckResult:
    identifiers = inspector.ids | inspector.classes
    has_restart_identifier = any(
        keyword in identifier
        for identifier in identifiers
        for keyword in ("restart", "reset", "again")
    )
    has_restart_text = any(
        "重新" in text or "restart" in text or "reset" in text
        for text in inspector.button_texts
    )
    passed = has_restart_identifier or has_restart_text

    return StaticCheckResult(
        name="页面包含重新开始按钮",
        passed=passed,
        expected="HTML 中存在重新开始按钮",
        actual="找到重新开始按钮" if passed else "未找到重新开始按钮",
        detail="重新开始按钮用于游戏结束后恢复初始状态。",
        severity="medium",
        suggestion='添加按钮，例如 <button id="restart">重新开始</button>。',
    )


def _check_direction_key_listener(javascript: str) -> StaticCheckResult:
    lowered = javascript.lower()
    has_keydown = "keydown" in lowered
    direction_hits = sum(
        1
        for keyword in ("arrowup", "arrowdown", "arrowleft", "arrowright", "keycode")
        if keyword in lowered
    )
    passed = has_keydown and direction_hits >= 2

    return StaticCheckResult(
        name="JS 包含方向键监听",
        passed=passed,
        expected="script.js 中监听 keydown，并处理方向键",
        actual="找到方向键监听" if passed else "未找到完整的方向键监听逻辑",
        detail=f"keydown={has_keydown}，方向键命中特征数={direction_hits}。",
        severity="high",
        suggestion="在 script.js 中使用 document.addEventListener('keydown', ...) 处理 ArrowUp/ArrowDown/ArrowLeft/ArrowRight。",
    )


def _check_collision_logic(javascript: str) -> StaticCheckResult:
    lowered = javascript.lower()
    has_collision_name = any(
        keyword in lowered
        for keyword in ("collision", "collide", "gameover", "game_over", "撞")
    )
    has_boundary_check = any(
        keyword in lowered
        for keyword in (">= tile", "< 0", "wall", "边界", "墙")
    )
    has_self_check = any(
        keyword in lowered
        for keyword in ("self", "some(", "slice(", "自身", "自己")
    )
    passed = has_collision_name and (has_boundary_check or has_self_check)

    return StaticCheckResult(
        name="JS 包含碰撞检测",
        passed=passed,
        expected="script.js 中存在撞墙或撞到自身后的游戏结束逻辑",
        actual="找到碰撞检测逻辑" if passed else "未找到明确的碰撞检测逻辑",
        detail=f"碰撞命名={has_collision_name}，边界检测={has_boundary_check}，自身检测={has_self_check}。",
        severity="high",
        suggestion="增加墙壁边界判断和蛇身重叠判断，碰撞后设置 gameOver 并停止游戏循环。",
    )


def _check_scoring_logic(javascript: str) -> StaticCheckResult:
    lowered = javascript.lower()
    has_score_state = "score" in lowered or "分数" in javascript
    has_score_increment = any(keyword in lowered for keyword in ("score +=", "score++", "score = score +"))
    has_score_render = any(
        keyword in lowered
        for keyword in ("textcontent", "innertext", "innerhtml")
    )
    passed = has_score_state and has_score_increment and has_score_render

    return StaticCheckResult(
        name="JS 包含计分逻辑",
        passed=passed,
        expected="script.js 中存在分数状态、加分逻辑和页面更新逻辑",
        actual="找到计分逻辑" if passed else "未找到完整的计分逻辑",
        detail=f"分数状态={has_score_state}，加分={has_score_increment}，页面更新={has_score_render}。",
        severity="high",
        suggestion="在吃到食物时增加 score，并同步更新页面上的分数元素。",
    )


def _is_same_file(value: str | None, expected_name: str) -> bool:
    if not value:
        return False
    return Path(value.split("?")[0].split("#")[0]).name.lower() == expected_name


def _build_summary(
    project_root: str | Path,
    passed: bool,
    passed_count: int,
    failed_count: int,
) -> str:
    status = "通过" if passed else "未通过"
    return (
        f"阶段 5A 静态测试{status}。"
        f"测试目录：{project_root}；通过 {passed_count} 项，失败 {failed_count} 项。"
    )
