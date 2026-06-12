"""验证阶段 5E 自动修复循环。"""

from __future__ import annotations

import shutil
import unittest

from schemas import CodeManifest, GeneratedFile, RepairRequest
from tools.file_io import read_json_file, resolve_project_path, write_text_file
from workflow.mock_demo import build_mock_architecture, build_mock_requirement
from workflow.repair import run_auto_repair_loop


class AutoRepairLoopTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_root = resolve_project_path("tmp/auto-repair")
        if self.tmp_root.exists():
            shutil.rmtree(self.tmp_root)

        self.requirement = build_mock_requirement()
        self.architecture = build_mock_architecture()

    def tearDown(self) -> None:
        if self.tmp_root.exists():
            shutil.rmtree(self.tmp_root)

    def test_auto_repair_skips_when_initial_tests_pass(self) -> None:
        """初始测试通过时，不应调用开发修复任务。"""

        project_root = "tmp/auto-repair/pass"
        self._write_complete_project(project_root)
        calls: list[int] = []

        def repair_executor(_request: RepairRequest, round_index: int) -> CodeManifest:
            calls.append(round_index)
            return self._complete_manifest(project_root)

        result = run_auto_repair_loop(
            requirement=self.requirement,
            architecture=self.architecture,
            project_root=project_root,
            max_rounds=2,
            repair_executor=repair_executor,
        )

        self.assertTrue(result.passed)
        self.assertEqual(result.rounds_used, 0)
        self.assertEqual(calls, [])
        self.assertEqual(result.records, [])

    def test_auto_repair_stops_after_successful_first_round(self) -> None:
        """第一轮修复后测试通过时，应立即结束循环。"""

        project_root = "tmp/auto-repair/one-round"
        self._write_broken_project(project_root)
        calls: list[int] = []

        def repair_executor(request: RepairRequest, round_index: int) -> CodeManifest:
            calls.append(round_index)
            self.assertGreater(len(request.defects), 0)
            return self._complete_manifest(project_root)

        result = run_auto_repair_loop(
            requirement=self.requirement,
            architecture=self.architecture,
            project_root=project_root,
            max_rounds=2,
            repair_executor=repair_executor,
        )
        report = read_json_file("reports/test_report.json")

        self.assertTrue(result.passed)
        self.assertEqual(result.rounds_used, 1)
        self.assertEqual(calls, [1])
        self.assertEqual(len(result.records), 1)
        self.assertTrue(report["passed"])

    def test_auto_repair_uses_at_most_two_rounds(self) -> None:
        """持续失败时，自动修复最多执行 2 轮。"""

        project_root = "tmp/auto-repair/still-failing"
        self._write_broken_project(project_root)
        calls: list[int] = []

        def repair_executor(_request: RepairRequest, round_index: int) -> CodeManifest:
            calls.append(round_index)
            return self._broken_manifest(project_root)

        result = run_auto_repair_loop(
            requirement=self.requirement,
            architecture=self.architecture,
            project_root=project_root,
            max_rounds=2,
            repair_executor=repair_executor,
        )

        self.assertFalse(result.passed)
        self.assertEqual(result.rounds_used, 2)
        self.assertEqual(calls, [1, 2])
        self.assertEqual(len(result.records), 2)
        self.assertGreater(result.final_report.failed_count, 0)

    def _write_broken_project(self, project_root: str) -> None:
        write_text_file(
            f"{project_root}/index.html",
            "<html><body><h1>贪吃蛇</h1></body></html>\n",
        )

    def _write_complete_project(self, project_root: str) -> None:
        manifest = self._complete_manifest(project_root)
        for file in manifest.files:
            write_text_file(file.path, file.content)

    def _broken_manifest(self, project_root: str) -> CodeManifest:
        return CodeManifest(
            project_name="broken-snake",
            project_root=project_root,
            entry_point=f"{project_root}/index.html",
            run_instruction="打开 index.html",
            files=[
                GeneratedFile(
                    path=f"{project_root}/index.html",
                    purpose="入口页面",
                    language="html",
                    content="<html><body><h1>贪吃蛇</h1></body></html>\n",
                )
            ],
        )

    def _complete_manifest(self, project_root: str) -> CodeManifest:
        return CodeManifest(
            project_name="snake-game",
            project_root=project_root,
            entry_point=f"{project_root}/index.html",
            run_instruction="打开 index.html",
            files=[
                GeneratedFile(
                    path=f"{project_root}/index.html",
                    purpose="页面结构",
                    language="html",
                    content="""<!doctype html>
<html lang="zh-CN">
<head><link rel="stylesheet" href="style.css"></head>
<body>
  <canvas id="game"></canvas>
  <div class="score">分数：<span id="score">0</span></div>
  <button id="restart">重新开始</button>
  <script src="script.js"></script>
</body>
</html>
""",
                ),
                GeneratedFile(
                    path=f"{project_root}/style.css",
                    purpose="页面样式",
                    language="css",
                    content="canvas { display: block; }\n",
                ),
                GeneratedFile(
                    path=f"{project_root}/script.js",
                    purpose="游戏逻辑",
                    language="javascript",
                    content="""let score = 0;
let gameOver = false;
document.addEventListener("keydown", (event) => {
  if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(event.key)) {
    event.preventDefault();
  }
});
function isWallCollision(head) {
  return head.x < 0 || head.y < 0 || head.x >= tileCount || head.y >= tileCount;
}
function isSelfCollision(head) {
  return snake.some((part) => part.x === head.x && part.y === head.y);
}
function addScore() {
  score += 10;
  document.getElementById("score").textContent = String(score);
}
""",
                ),
            ],
        )


if __name__ == "__main__":
    unittest.main()
