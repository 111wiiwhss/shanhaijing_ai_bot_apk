
# Pixel Mecha Fighter

一个使用 Kivy 开发的像素风格机甲对战游戏，支持同屏双人对战！

## 🎮 游戏特性

- **同屏双人对战**：两个玩家可以在同一台设备上对战
- **精美像素风格**：完全程序化绘制的像素机甲和场景
- **丰富的动作系统**：
  - 移动（左右摇杆）
  - 跳跃（可二段跳）
  - 冲刺（消耗耐力）
  - 轻攻击（快速出招，可连击）
  - 重攻击（高伤害，硬直长）
  - 防御（格挡，消耗耐力）
  - 必杀技（全屏高伤害，能量满时可用）
- **完整的游戏循环**：标题画面 → 倒计时 → 战斗 → 胜负判定 → 重新开始
- **视觉效果**：粒子特效、连击显示、完整的 HUD（生命/能量/耐力条）

## 🛠️ 技术栈

- **Python 3**：核心编程语言
- **Kivy**：跨平台 GUI 框架，提供图形渲染和输入处理
- **Canvas 指令**：所有游戏元素均使用 Kivy 的 Canvas 系统程序化绘制，无需外部图片资源

## 📦 安装和运行

### 1. 系统依赖（Linux）

在运行游戏前，需要先安装一些系统依赖：

```bash
sudo apt-get update
sudo apt-get install -y libgl1-mesa-dev libgles2-mesa-dev \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
    zlib1g-dev libmtdev-dev
```

### 2. Python 依赖

安装 Python 包：

```bash
pip install -r requirements.txt
```

或者直接安装 Kivy：

```bash
pip install kivy[base] --prefer-binary
```

### 3. 运行游戏

```bash
python run_game.py
```

或者直接从 kivy_app 目录运行：

```bash
cd kivy_app
python main.py
```

## 🎯 游戏操作

### 玩家 1（蓝色机甲）

- **左侧虚拟摇杆**：控制移动方向
- **操作按钮**（从左到右，从上到下）：
  - JMP：跳跃
  - L-ATK：轻攻击
  - GRD：防御
  - H-ATK：重攻击
  - DSH：冲刺
  - SPC：必杀技（能量满时）

### 玩家 2（红色机甲）

- **右侧虚拟摇杆**：控制移动方向
- **操作按钮**：与玩家 1 相同的布局（镜像对称）

## 🏗️ 项目结构

```
/workspace/
├── kivy_app/
│   ├── main.py           # 游戏入口，UI 布局和触摸控制
│   └── game/
│       ├── __init__.py   # 包初始化
│       ├── fighter.py    # 机甲角色数据和状态机
│       ├── combat.py     # 战斗系统：碰撞检测、伤害计算
│       ├── controls.py   # 虚拟摇杆和按钮控件
│       ├── sprites.py    # 像素精灵渲染和动画系统
│       ├── scene.py      # 场景背景和粒子特效
│       ├── ui.py         # HUD 界面（血条、能量条等）
│       └── engine.py     # 游戏引擎主循环和状态管理
├── docs/                 # 设计文档
├── requirements.txt      # Python 依赖
└── run_game.py          # 游戏运行脚本
```

## 📐 游戏规则

1. **生命值**：每个机甲有 100 点生命值，归零即输掉比赛
2. **能量**：攻击命中敌人或受到攻击会获得能量，满 100 点可使用必杀技
3. **耐力**：冲刺和防御会消耗耐力，每秒自动恢复，耗尽时无法使用相关技能
4. **连击**：连续轻攻击命中敌人可触发连击，获得额外伤害加成
5. **无敌时间**：受到伤害后会有短暂的无敌时间

## 🎨 设计文档

项目包含详细的设计文档，位于 `docs/` 目录下：
- `plans/`：实现计划
- `specs/`：设计规格说明

## 📝 许可证

MIT License
