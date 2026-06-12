"""本地 Mock 贪吃蛇 Demo。

这个文件用于没有模型密钥时验证阶段 4D 的产物保存链路。
它不替代真实 CrewAI 执行，只提供一组确定性的结构化产物。
"""

from __future__ import annotations

from pathlib import Path

from schemas import (
    AcceptanceCriterion,
    ArchitecturePlan,
    CodeManifest,
    FeatureRequirement,
    FileDesign,
    GeneratedFile,
    ModuleDesign,
    RequirementDocument,
    UserInteraction,
)
from tools.artifact_writer import (
    save_architecture_plan,
    save_code_manifest,
    save_requirement_document,
    save_test_report,
)
from tools.test_runner import run_predefined_test_cases


def build_mock_requirement() -> RequirementDocument:
    """构造示例需求文档。"""

    return RequirementDocument(
        app_name="贪吃蛇游戏",
        summary="生成一个可直接在浏览器中运行的贪吃蛇 HTML 游戏。",
        target_users=["想快速体验小游戏的普通用户", "用于验证 Agent 开发流程的学习者"],
        features=[
            FeatureRequirement(
                name="方向键控制",
                description="玩家可以使用键盘方向键控制蛇向上、下、左、右移动。",
                priority="high",
            ),
            FeatureRequirement(
                name="食物与计分",
                description="蛇吃到食物后身体变长，分数增加，并刷新新的食物位置。",
                priority="high",
            ),
            FeatureRequirement(
                name="碰撞结束",
                description="蛇撞到墙壁或自己的身体后，游戏进入结束状态。",
                priority="high",
            ),
            FeatureRequirement(
                name="重新开始",
                description="游戏结束后，玩家可以点击按钮重置游戏状态并重新开始。",
                priority="medium",
            ),
        ],
        user_interactions=[
            UserInteraction(action="按下方向键", expected_result="蛇的移动方向发生变化"),
            UserInteraction(action="点击重新开始按钮", expected_result="分数清零，蛇和食物回到初始状态"),
        ],
        acceptance_criteria=[
            AcceptanceCriterion(criterion="页面能正常打开，并显示游戏区域、分数和重新开始按钮。"),
            AcceptanceCriterion(criterion="方向键可以控制蛇移动，且不能直接反向穿过自身。"),
            AcceptanceCriterion(criterion="蛇吃到食物后分数增加，身体变长。"),
            AcceptanceCriterion(criterion="蛇撞墙或撞到自己后显示游戏结束状态。"),
        ],
    )


def build_mock_architecture() -> ArchitecturePlan:
    """构造示例架构方案。"""

    return ArchitecturePlan(
        tech_stack=["HTML", "CSS", "JavaScript"],
        files=[
            FileDesign(path="generated/snake-game/index.html", responsibility="定义页面结构和游戏画布。"),
            FileDesign(path="generated/snake-game/style.css", responsibility="定义游戏页面布局、按钮和状态样式。"),
            FileDesign(path="generated/snake-game/script.js", responsibility="实现游戏状态、输入控制、渲染、碰撞和重启逻辑。"),
        ],
        modules=[
            ModuleDesign(name="状态管理", responsibility="维护蛇、食物、方向、分数和游戏状态。"),
            ModuleDesign(name="输入控制", responsibility="监听方向键，更新下一步移动方向。", dependencies=["状态管理"]),
            ModuleDesign(name="游戏循环", responsibility="按固定时间推进游戏状态。", dependencies=["状态管理", "碰撞检测"]),
            ModuleDesign(name="碰撞检测", responsibility="判断蛇是否撞墙或撞到自身。", dependencies=["状态管理"]),
            ModuleDesign(name="渲染模块", responsibility="把当前游戏状态绘制到 canvas。", dependencies=["状态管理"]),
        ],
        data_flow=[
            "用户按方向键，输入控制模块更新 pendingDirection。",
            "游戏循环读取方向并移动蛇头。",
            "状态管理判断是否吃到食物，更新蛇身和分数。",
            "碰撞检测判断游戏是否结束。",
            "渲染模块根据最新状态重绘画布和分数。",
        ],
        implementation_notes=[
            "使用 canvas 绘制网格、蛇和食物。",
            "使用 setInterval 实现固定速度的游戏循环。",
            "禁止玩家直接反向移动，避免蛇立即撞到自己。",
            "重新开始时需要清理旧计时器并重置所有状态。",
        ],
    )


def build_mock_code_manifest() -> CodeManifest:
    """构造示例代码清单和源码内容。"""

    html = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>贪吃蛇游戏</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main class="app">
    <section class="topbar">
      <div>
        <h1>贪吃蛇</h1>
        <p id="status">使用方向键开始移动</p>
      </div>
      <div class="score">分数：<span id="score">0</span></div>
    </section>
    <canvas id="game" width="480" height="480" aria-label="贪吃蛇游戏区域"></canvas>
    <button id="restart" type="button">重新开始</button>
  </main>
  <script src="script.js"></script>
</body>
</html>
"""

    css = """* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-height: 100vh;
  display: grid;
  place-items: center;
  font-family: Arial, "Microsoft YaHei", sans-serif;
  background: #eef2f3;
  color: #1f2933;
}

.app {
  width: min(92vw, 560px);
  display: grid;
  gap: 14px;
}

.topbar {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 16px;
}

h1 {
  margin: 0 0 4px;
  font-size: 30px;
}

p {
  margin: 0;
  color: #52616b;
}

.score {
  font-size: 20px;
  font-weight: 700;
}

canvas {
  width: 100%;
  aspect-ratio: 1;
  display: block;
  border: 3px solid #1f2933;
  background: #f8fafc;
}

button {
  justify-self: start;
  padding: 10px 18px;
  border: 0;
  border-radius: 6px;
  background: #2563eb;
  color: white;
  font-size: 16px;
  cursor: pointer;
}

button:hover {
  background: #1d4ed8;
}
"""

    javascript = """const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const scoreEl = document.getElementById("score");
const statusEl = document.getElementById("status");
const restartBtn = document.getElementById("restart");

const gridSize = 24;
const tileCount = canvas.width / gridSize;
const tickMs = 120;

let snake;
let food;
let direction;
let pendingDirection;
let score;
let gameOver;
let timerId;

function resetGame() {
  snake = [
    { x: 8, y: 10 },
    { x: 7, y: 10 },
    { x: 6, y: 10 },
  ];
  direction = { x: 1, y: 0 };
  pendingDirection = { x: 1, y: 0 };
  score = 0;
  gameOver = false;
  scoreEl.textContent = String(score);
  statusEl.textContent = "使用方向键开始移动";
  placeFood();
  draw();
  clearInterval(timerId);
  timerId = setInterval(tick, tickMs);
}

function placeFood() {
  do {
    food = {
      x: Math.floor(Math.random() * tileCount),
      y: Math.floor(Math.random() * tileCount),
    };
  } while (snake.some((part) => part.x === food.x && part.y === food.y));
}

function tick() {
  if (gameOver) {
    return;
  }

  direction = pendingDirection;
  const head = {
    x: snake[0].x + direction.x,
    y: snake[0].y + direction.y,
  };

  if (isWallCollision(head) || isSelfCollision(head)) {
    endGame();
    return;
  }

  snake.unshift(head);

  if (head.x === food.x && head.y === food.y) {
    score += 10;
    scoreEl.textContent = String(score);
    placeFood();
  } else {
    snake.pop();
  }

  draw();
}

function isWallCollision(head) {
  return head.x < 0 || head.y < 0 || head.x >= tileCount || head.y >= tileCount;
}

function isSelfCollision(head) {
  return snake.some((part) => part.x === head.x && part.y === head.y);
}

function endGame() {
  gameOver = true;
  clearInterval(timerId);
  statusEl.textContent = "游戏结束，点击重新开始";
  draw();
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "#e5e7eb";
  for (let index = 0; index <= tileCount; index += 1) {
    const position = index * gridSize;
    ctx.fillRect(position, 0, 1, canvas.height);
    ctx.fillRect(0, position, canvas.width, 1);
  }

  ctx.fillStyle = "#ef4444";
  ctx.fillRect(food.x * gridSize + 3, food.y * gridSize + 3, gridSize - 6, gridSize - 6);

  snake.forEach((part, index) => {
    ctx.fillStyle = index === 0 ? "#15803d" : "#22c55e";
    ctx.fillRect(part.x * gridSize + 2, part.y * gridSize + 2, gridSize - 4, gridSize - 4);
  });

  if (gameOver) {
    ctx.fillStyle = "rgba(15, 23, 42, 0.72)";
    ctx.fillRect(0, canvas.height / 2 - 34, canvas.width, 68);
    ctx.fillStyle = "#ffffff";
    ctx.font = "28px Arial";
    ctx.textAlign = "center";
    ctx.fillText("Game Over", canvas.width / 2, canvas.height / 2 + 10);
  }
}

function changeDirection(nextDirection) {
  const isReverse =
    nextDirection.x + direction.x === 0 && nextDirection.y + direction.y === 0;

  if (!isReverse) {
    pendingDirection = nextDirection;
    statusEl.textContent = "游戏进行中";
  }
}

document.addEventListener("keydown", (event) => {
  const keyMap = {
    ArrowUp: { x: 0, y: -1 },
    ArrowDown: { x: 0, y: 1 },
    ArrowLeft: { x: -1, y: 0 },
    ArrowRight: { x: 1, y: 0 },
  };

  if (keyMap[event.key]) {
    event.preventDefault();
    changeDirection(keyMap[event.key]);
  }
});

restartBtn.addEventListener("click", resetGame);

resetGame();
"""

    return CodeManifest(
        project_name="snake-game",
        project_root="generated/snake-game",
        entry_point="generated/snake-game/index.html",
        run_instruction="在浏览器中打开 generated/snake-game/index.html",
        files=[
            GeneratedFile(
                path="generated/snake-game/index.html",
                purpose="页面结构",
                language="html",
                content=html,
            ),
            GeneratedFile(
                path="generated/snake-game/style.css",
                purpose="页面样式",
                language="css",
                content=css,
            ),
            GeneratedFile(
                path="generated/snake-game/script.js",
                purpose="游戏逻辑",
                language="javascript",
                content=javascript,
            ),
        ],
    )


def run_mock_snake_demo() -> list[Path]:
    """生成本地 Mock 产物，并使用本地 Test Runner 生成最终测试报告。"""

    requirement = build_mock_requirement()
    architecture = build_mock_architecture()
    code_manifest = build_mock_code_manifest()

    written_files: list[Path] = []
    written_files.extend(save_requirement_document(requirement))
    written_files.extend(save_architecture_plan(architecture))
    written_files.extend(save_code_manifest(code_manifest))

    test_report = run_predefined_test_cases(code_manifest.project_root)
    written_files.extend(save_test_report(test_report))

    return written_files
