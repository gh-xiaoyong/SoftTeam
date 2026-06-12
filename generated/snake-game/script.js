(function() {
    'use strict';

    // ========== 配置常量 ==========
    const GRID_SIZE = 20;          // 20x20 网格
    const CELL_SIZE = 20;          // 像素
    const TICK_INTERVAL = 200;     // 毫秒

    // ========== DOM 元素引用 ==========
    const canvas = document.getElementById('game-canvas');
    const ctx = canvas.getContext('2d');
    const scoreDisplay = document.getElementById('score-display');
    const gameOverOverlay = document.getElementById('game-over-overlay');
    const restartBtn = document.getElementById('restart-btn');

    // ========== 游戏状态 ==========
    let snake = [];               // 蛇身坐标数组 [x,y]，索引0为蛇头
    let food = { x: 0, y: 0 };    // 食物坐标
    let direction = 'RIGHT';      // 当前移动方向
    let nextDirection = 'RIGHT';  // 下一个有效方向（防止反向）
    let directionQueue = [];      // 方向队列，长度最多2
    let score = 0;
    let gameRunning = false;
    let gameLoopId = null;

    // ========== 初始化 ==========
    function initGame() {
        // 蛇初始位置：水平3节，方向向右
        snake = [
            [10, 10],
            [9, 10],
            [8, 10]
        ];
        direction = 'RIGHT';
        nextDirection = 'RIGHT';
        directionQueue = [];
        score = 0;
        scoreDisplay.textContent = score;
        gameOverOverlay.classList.add('hidden');
        generateFood();
        draw();
    }

    // ========== 食物生成 ==========
    function generateFood() {
        const occupied = new Set();
        snake.forEach(segment => occupied.add(`${segment[0]},${segment[1]}`));
        const freeCells = [];
        for (let x = 0; x < GRID_SIZE; x++) {
            for (let y = 0; y < GRID_SIZE; y++) {
                if (!occupied.has(`${x},${y}`)) {
                    freeCells.push({ x, y });
                }
            }
        }
        if (freeCells.length === 0) {
            // 没有空白格子（理论上蛇占满所有格子时触发，但游戏通常在此之前结束）
            return;
        }
        const randomIndex = Math.floor(Math.random() * freeCells.length);
        food = freeCells[randomIndex];
    }

    // ========== 蛇移动与碰撞检测 ==========
    function moveSnake() {
        // 从方向队列取出第一个方向
        if (directionQueue.length > 0) {
            const newDirection = directionQueue.shift();
            // 检查是否与当前方向相反
            const opposites = {
                'UP': 'DOWN',
                'DOWN': 'UP',
                'LEFT': 'RIGHT',
                'RIGHT': 'LEFT'
            };
            if (newDirection !== opposites[direction]) {
                direction = newDirection;
            }
        }

        // 计算新蛇头坐标
        const head = snake[0];
        let newHeadX = head[0];
        let newHeadY = head[1];
        switch (direction) {
            case 'UP':    newHeadY--; break;
            case 'DOWN':  newHeadY++; break;
            case 'LEFT':  newHeadX--; break;
            case 'RIGHT': newHeadX++; break;
        }

        // 检查是否吃到食物
        const ateFood = (newHeadX === food.x && newHeadY === food.y);

        // 构建新身体（先加头，再决定是否去尾）
        const newSnake = [[newHeadX, newHeadY]].concat(snake);
        if (!ateFood) {
            newSnake.pop();
        }
        snake = newSnake;

        // 如果吃到食物，更新分数并生成新食物
        if (ateFood) {
            score++;
            scoreDisplay.textContent = score;
            generateFood();
        }

        // 碰撞检测
        const headPos = snake[0];
        // 撞墙
        if (headPos[0] < 0 || headPos[0] >= GRID_SIZE || headPos[1] < 0 || headPos[1] >= GRID_SIZE) {
            return 'wall';
        }
        // 撞自身（排除蛇头本身，检查后面是否有相同坐标）
        for (let i = 1; i < snake.length; i++) {
            if (snake[i][0] === headPos[0] && snake[i][1] === headPos[1]) {
                return 'self';
            }
        }
        return 'ok';
    }

    // ========== 游戏循环 tick ==========
    function gameTick() {
        if (!gameRunning) return;
        const result = moveSnake();
        if (result === 'wall' || result === 'self') {
            gameOver();
        } else {
            draw();
        }
    }

    // ========== 游戏结束 ==========
    function gameOver() {
        gameRunning = false;
        if (gameLoopId) {
            clearInterval(gameLoopId);
            gameLoopId = null;
        }
        gameOverOverlay.classList.remove('hidden');
        draw(); // 重绘显示最终状态
    }

    // ========== 渲染 ==========
    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // 绘制网格线（可选）
        ctx.strokeStyle = '#1b2a4a';
        ctx.lineWidth = 0.5;
        for (let x = 0; x <= GRID_SIZE; x++) {
            ctx.beginPath();
            ctx.moveTo(x * CELL_SIZE, 0);
            ctx.lineTo(x * CELL_SIZE, canvas.height);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(0, x * CELL_SIZE);
            ctx.lineTo(canvas.width, x * CELL_SIZE);
            ctx.stroke();
        }

        // 绘制蛇
        snake.forEach((segment, index) => {
            const [x, y] = segment;
            ctx.fillStyle = index === 0 ? '#2ecc71' : '#27ae60';
            ctx.fillRect(x * CELL_SIZE + 1, y * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2);
        });

        // 绘制食物
        ctx.fillStyle = '#e74c3c';
        ctx.beginPath();
        ctx.arc(food.x * CELL_SIZE + CELL_SIZE/2, food.y * CELL_SIZE + CELL_SIZE/2, CELL_SIZE/2 - 2, 0, Math.PI * 2);
        ctx.fill();
    }

    // ========== 键盘事件处理 ==========
    function handleKeyDown(e) {
        if (!gameRunning) return;

        const key = e.key;
        const directionMap = {
            'ArrowUp': 'UP',
            'ArrowDown': 'DOWN',
            'ArrowLeft': 'LEFT',
            'ArrowRight': 'RIGHT'
        };
        if (directionMap.hasOwnProperty(key)) {
            e.preventDefault();
            const newDir = directionMap[key];
            // 防止反向：检查新方向是否与当前方向相反
            const opposites = {
                'UP': 'DOWN',
                'DOWN': 'UP',
                'LEFT': 'RIGHT',
                'RIGHT': 'LEFT'
            };
            // 如果方向队列为空，检查新方向是否与 current direction 相反
            // 如果队列非空，检查新方向是否与队列最后一个方向相反
            const lastDir = directionQueue.length > 0 ? directionQueue[directionQueue.length - 1] : direction;
            if (newDir !== opposites[lastDir]) {
                if (directionQueue.length < 2) {
                    directionQueue.push(newDir);
                }
            }
        }
    }

    // ========== 重新开始 ==========
    function restart() {
        // 停止当前循环
        if (gameLoopId) {
            clearInterval(gameLoopId);
            gameLoopId = null;
        }
        gameRunning = false;
        initGame();
        // 启动游戏循环
        startGameLoop();
    }

    // ========== 启动游戏循环 ==========
    function startGameLoop() {
        if (gameLoopId) {
            clearInterval(gameLoopId);
        }
        gameRunning = true;
        gameLoopId = setInterval(gameTick, TICK_INTERVAL);
    }

    // ========== 事件绑定 ==========
    document.addEventListener('keydown', handleKeyDown);
    restartBtn.addEventListener('click', restart);

    // ========== 启动游戏 ==========
    initGame();
    startGameLoop();

})();