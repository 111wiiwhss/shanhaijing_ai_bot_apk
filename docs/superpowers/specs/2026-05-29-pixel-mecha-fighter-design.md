# Pixel Mecha Fighter - 设计规格

## 概述

一款像素风格的机甲对战小游戏。两个机甲在同一屏幕上对战，玩家各自操作一套虚拟操控（摇杆+按钮），通过移动、跳跃、冲刺、攻击、防御等操作将对方击败。画面采用复古像素风格，所有精灵由 Kivy Canvas 指令程序化绘制，不依赖外部图片资源。

## 技术决策

| 决策项 | 选择 |
|---|---|
| 平台/框架 | Kivy / Python |
| 架构模式 | 模块化游戏架构（按职责拆分为独立模块） |
| 对战模式 | 同屏双人（左右各一套虚拟操控） |
| 战斗系统 | 进阶版（移动/跳跃/冲刺/轻攻击/重攻击/防御/必杀技/连招） |
| 美术方案 | 程序化像素绘制，完整精灵帧动画（每机甲约 38 帧） |
| 场景 | 城市废墟，320×180 逻辑分辨率 |
| 机甲 | 蓝方"冰刃" vs 红方"炎拳" |

---

## 游戏玩法设计

### 战场与角色

- 场景：城市废墟像素风背景（320×180 逻辑分辨率，等比缩放适配屏幕）
- 玩家 1（蓝方"冰刃"）左侧，玩家 2（红方"炎拳"）右侧
- 角色自动面朝对手方向检测

### 移动与机动

| 动作 | 操作 | 说明 |
|---|---|---|
| 移动 | 虚拟摇杆 | 左右移动，靠近对手 |
| 跳跃 | 跳跃按钮 | 单击一次跳跃，空中可二段跳 |
| 冲刺 | 冲刺按钮 / 双击方向 | 快速位移，消耗 20 点耐力 |

### 战斗系统

| 动作 | 操作 | 说明 |
|---|---|---|
| 轻攻击 | 轻攻击按钮 | 出招快（8帧）、伤害 5、可连击 |
| 重攻击 | 重攻击按钮 | 出招慢（14帧）、伤害 12、硬直时间长 |
| 防御 | 防御按钮（按住） | 格挡正面攻击，格挡成功减伤 80%，消耗 5 耐力/次 |
| 必杀技 | 必杀技按钮（能量满时） | 全屏大伤害（25），不可格挡，消耗全部能量 |

### 连招逻辑

- 轻攻击有连击判定窗口（命中后 18 帧内再次轻攻击触发连击）
- 连击数显示在 HUD
- 第 3 连击附带额外伤害加成（+3）
- 受击或超过连击窗口则连击中断

### 属性状态

| 属性 | 最大值 | 说明 |
|---|---|---|
| HP | 100 | 降为 0 即失败 |
| 能量槽 | 100 | 攻击命中 +10，受击 +15，满格可放必杀 |
| 耐力 | 100 | 防御 -5/次，冲刺 -20，每秒恢复 8 |

---

## 核心代码结构

```
kivy_app/
├── main.py                  # 入口，Kivy App 类，返回 GameScreen
├── game/
│   ├── engine.py            # GameWidget - 游戏主容器，60fps 时钟驱动
│   ├── fighter.py           # Fighter 数据类 (hp, energy, stamina, pos, state)
│   ├── combat.py            # 战斗判定 (hitbox, damage, combo, guard)
│   ├── controls.py          # VirtualStick + ActionButton 自定义 Widget
│   ├── sprites.py           # 帧动画管理器，程序化像素精灵绘制
│   ├── scene.py             # 城市废墟背景、地面、粒子特效
│   └── ui.py                # HUD：血条、能量槽、耐力槽、胜负弹窗
```

### 模块职责

#### engine.py — 游戏引擎
- `GameWidget(Widget)` — 顶层容器
- `Clock.schedule_interval(self.update, 1/60)` 驱动 60fps 主循环
- 管理 `GameState` 枚举：`IDLE → COUNTDOWN → FIGHTING → WINNER`
- 每帧调用各子模块的 update()

#### fighter.py — 机甲实体
- `FighterState` 枚举：`IDLE | WALK | JUMP | DASH | LIGHT_ATTACK | HEAVY_ATTACK | GUARD | HURT | SPECIAL`
- `Fighter` 数据类：
  - 属性：`hp=100, max_hp=100, energy=0, max_energy=100, stamina=100, max_stamina=100`
  - 位置：`x, y, vx, vy`
  - 状态：`state, facing, on_ground, combo_count, invincible_timer`
  - 方法：`take_damage(amount)`, `update(dt)`

#### combat.py — 战斗系统
- `Hitbox`：位置 + 宽高矩形
- `CombatSystem`：
  - `check_hit(attacker, defender)` → 检测攻击 hitbox 与防御方受击框是否相交
  - `calculate_damage(attack_type, is_guarding, combo_count)` → 返回最终伤害
  - `update_combo(attacker, dt)` → 管理连击窗口

#### controls.py — 输入系统
- `VirtualStick(Widget)` — 触摸拖拽型虚拟摇杆
  - 中心死区半径 8px
  - 输出归一化方向 `(dx, dy)`
- `ActionButton(Widget)` — 单动作按钮
  - 支持 `on_press` / `on_release`
- `ControlState` — 每个玩家一套：
  - `direction: tuple[float, float]`
  - `jump: bool`, `light_attack: bool`, `heavy_attack: bool`
  - `guard: bool`, `dash: bool`, `special: bool`

#### sprites.py — 精灵动画
- `PixelSprite` — 程序化绘制类
  - 每个机甲状态对应一个绘制方法，按帧序号返回不同像素图案
  - 使用 Kivy Canvas `Rectangle` 和 `Color` 指令
  - 调色板：蓝方 16 色调色板（蓝/青/白系），红方 16 色调色板（红/橙/黄系）
- `SpriteAnimator` — 帧动画控制器
  - 当前状态 → 当前帧 → 帧切换计时 → 动画完成回调
- 精灵帧规格：机甲 32×32 像素，8-12 fps 切换

#### scene.py — 场景渲染
- 城市废墟背景层：
  - 天空梯度（暗红紫 → 深灰）
  - 废墟建筑剪影（3 层视差：远/中/近）
  - 地面线 + 瓦砾碎片
- 粒子特效：
  - 命中火花粒子
  - 必杀技全屏闪光
  - 废墟火焰/烟雾
- 地面碰撞线：`ground_y = 156`（180 像素高度的底部 24 像素为地面区）

#### ui.py — HUD 系统
- 顶部 HUD 条：
  - P1 血条（左，蓝色）、P2 血条（右，红色）
  - 能量槽（对应颜色，满格时高亮）
  - 耐力槽（白色，消耗时闪烁）
- 连击计数器：角色上方浮字
- 回合结果弹窗："P1 WIN!" / "P2 WIN!" + "RESTART" 按钮

### 控制布局（同屏双人）

```
┌─────────────────────────────────────────────┐
│  [ 血条 P1 ]          [ 血条 P2 ]          │
│                                             │
│                游戏主区域                    │
│                                             │
│  [摇杆1]  [跳] [轻]  │  [轻] [跳]  [摇杆2] │
│  P1       [防] [重]  │  [重] [防]  P2      │
│           [冲] [必]  │  [必] [冲]           │
└─────────────────────────────────────────────┘
```

- 摇杆：屏幕左右下角 120×120 区域
- 按钮：摇杆内侧，60×60 区域
- P2 摇杆方向逻辑镜像

---

## 精灵帧清单

### 蓝方"冰刃"（共 38 帧）

| 动画状态 | 帧数 | 帧率(fps) | 说明 |
|---|---|---|---|
| idle | 4 | 6 | 站立呼吸浮动 |
| walk | 6 | 10 | 步行动画循环 |
| jump | 2 | - | 起跳/空中姿态 |
| dash | 4 | 12 | 冲刺残影 |
| light_attack | 4 | 12 | 快速斩击/出拳 |
| heavy_attack | 6 | 10 | 蓄力重斩 |
| guard | 2 | - | 护盾/格挡姿态 |
| hurt | 2 | - | 受击硬直 |
| special | 8 | 12 | 必杀技全屏特效 |
| **合计** | **38** | | |

### 红方"炎拳"（同上 38 帧，不同配色/造型）

总计 76 帧程序化像素精灵。

---

## 游戏流程

```
IDLE → 显示标题 "MECHA FIGHTER" + "TAP TO START"
  ↓ 双方点击就绪
COUNTDOWN → "3... 2... 1... FIGHT!"
  ↓
FIGHTING → 主战斗循环
  ↓ 一方 HP ≤ 0
WINNER → "P1 WIN!" / "P2 WIN!" + 倒计时自动重新开始
```

---

## 数据流

```
触摸事件 → controls.py (ControlState) → engine.py (输入分发)
                                            ↓
engine.py → fighter.py (Fighter.update) → 位置/状态更新
engine.py → combat.py (Hitbox检测) → 伤害/连招结果
engine.py → sprites.py (帧更新) → 渲染
engine.py → scene.py (特效更新) → 背景/粒子渲染
engine.py → ui.py (HUD更新) → 界面渲染
```

所有渲染使用 Kivy Canvas 指令，在 `GameWidget` 的 `canvas` 中统一绘制。

---

## 性能与约束

- 目标 60fps 稳定运行
- 精灵绘制使用预计算的顶点缓冲区
- 场景视差层不超过 3 层
- 粒子特效同时存在不超过 50 个
- 最小触摸响应距离 8px 死区