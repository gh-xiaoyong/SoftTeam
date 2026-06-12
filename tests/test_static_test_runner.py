"""验证阶段 5A 本地静态测试器。"""

from __future__ import annotations

import shutil
import unittest

from tools.file_io import resolve_project_path, write_text_file
from tools.static_test_runner import run_static_snake_tests


class StaticTestRunnerTest(unittest.TestCase):
    def setUp(self) -> None:
        """每个用例使用独立的临时项目目录，避免互相污染。"""

        self.tmp_root = resolve_project_path("tmp/static-test-runner")
        if self.tmp_root.exists():
            shutil.rmtree(self.tmp_root)

    def tearDown(self) -> None:
        if self.tmp_root.exists():
            shutil.rmtree(self.tmp_root)

    def test_static_tests_pass_for_complete_snake_project(self) -> None:
        """完整的 HTML/CSS/JS 结构应该通过全部静态检查。"""

        project_root = "tmp/static-test-runner/pass"
        write_text_file(
            f"{project_root}/index.html",
            """<!doctype html>
<html lang="zh-CN">
<head>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main>
    <canvas id="game"></canvas>
    <div class="score">分数：<span id="score">0</span></div>
    <button id="restart">重新开始</button>
  </main>
  <script src="script.js"></script>
</body>
</html>
""",
        )
        write_text_file(f"{project_root}/style.css", "canvas { display: block; }\n")
        write_text_file(
            f"{project_root}/script.js",
            """const scoreEl = document.getElementById("score");
let score = 0;
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

function eatFood() {
  score += 10;
  scoreEl.textContent = String(score);
}
""",
        )

        report = run_static_snake_tests(project_root)

        self.assertTrue(report.passed)
        self.assertEqual(report.total, 10)
        self.assertEqual(report.passed_count, 10)
        self.assertEqual(report.failed_count, 0)
        self.assertEqual(report.defects, [])

    def test_static_tests_return_defects_for_incomplete_project(self) -> None:
        """缺少关键文件和页面结构时，应返回可交给开发 Agent 的缺陷列表。"""

        project_root = "tmp/static-test-runner/fail"
        write_text_file(
            f"{project_root}/index.html",
            "<html><body><h1>贪吃蛇</h1></body></html>\n",
        )

        report = run_static_snake_tests(project_root)
        failed_case_names = {case.name for case in report.cases if not case.passed}

        self.assertFalse(report.passed)
        self.assertGreater(report.failed_count, 0)
        self.assertIn("style.css 文件存在", failed_case_names)
        self.assertIn("script.js 文件存在", failed_case_names)
        self.assertIn("页面包含游戏区域", failed_case_names)
        self.assertEqual(len(report.defects), report.failed_count)


if __name__ == "__main__":
    unittest.main()
