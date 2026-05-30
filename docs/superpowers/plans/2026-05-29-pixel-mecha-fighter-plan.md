# Pixel Mecha Fighter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a pixel-style two-player mecha fighting game on Kivy with virtual controls, combo system, and programmatic pixel art sprites.

**Architecture:** Modular game engine with 7 files under `game/` — fighter data model, combat system, input layer, sprite renderer, scene renderer, HUD, and the engine orchestrator. All rendering via Kivy Canvas instructions; no external image assets.

**Tech Stack:** Python 3, Kivy (UI + Canvas), pytest

---

## File Structure

```
kivy_app/
├── main.py                      # MODIFY: Replace with game entry point
├── game/
│   ├── __init__.py               # CREATE: Package init
│   ├── fighter.py                # CREATE: Fighter class + state machine
│   ├── combat.py                 # CREATE: Hitbox detection + damage calc
│   ├── controls.py               # CREATE: VirtualStick + ActionButton
│   ├── sprites.py                # CREATE: Programmatic pixel mecha renderer
│   ├── scene.py                  # CREATE: Background + particles
│   ├── ui.py                     # CREATE: HUD bars + win screen
│   └── engine.py                 # CREATE: GameWidget + main loop
```

**Dependency order:** fighter → combat, fighter+combat → engine, controls → engine, sprites → engine, scene → engine, ui → engine, engine → main

---

### Task 1: Project scaffolding and Fighter data model

**Files:**
- Create: `/workspace/kivy_app/game/__init__.py`
- Create: `/workspace/kivy_app/game/fighter.py`

- [ ] **Step 1: Create package init**

```python
# /workspace/kivy_app/game/__init__.py
```

- [ ] **Step 2: Write Fighter class with FighterState enum**

```python
# /workspace/kivy_app/game/fighter.py
from enum import Enum, auto
from dataclasses import dataclass, field

GROUND_Y = 156
ARENA_LEFT = 10
ARENA_RIGHT = 310
GRAVITY = 800
MOVE_SPEED = 120
JUMP_VELOCITY = 280
DASH_SPEED = 320
DASH_DURATION = 8
STAMINA_REGEN = 8
STAMINA_DASH_COST = 20
STAMINA_GUARD_COST = 5


class FighterState(Enum):
    IDLE = auto()
    WALK = auto()
    JUMP = auto()
    DASH = auto()
    LIGHT_ATTACK = auto()
    HEAVY_ATTACK = auto()
    GUARD = auto()
    HURT = auto()
    SPECIAL = auto()


@dataclass
class Fighter:
    player_id: int
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    facing_right: bool = True

    hp: int = 100
    max_hp: int = 100
    energy: int = 0
    max_energy: int = 100
    stamina: float = 100.0
    max_stamina: float = 100.0

    state: FighterState = FighterState.IDLE
    state_timer: int = 0
    on_ground: bool = True
    combo_count: int = 0
    combo_timer: int = 0
    invincible_timer: int = 0
    jump_count: int = 0
    is_guarding: bool = False
    attack_hit: bool = False

    def take_damage(self, amount: int):
        if self.invincible_timer > 0:
            return
        self.hp = max(0, self.hp - amount)
        self.energy = min(self.max_energy, self.energy + 15)
        self.state = FighterState.HURT
        self.state_timer = 12
        self.combo_count = 0
        self.combo_timer = 0
        self.invincible_timer = 6

    def spend_stamina(self, amount: float) -> bool:
        if self.stamina >= amount:
            self.stamina -= amount
            return True
        return False

    def add_energy(self, amount: int):
        self.energy = min(self.max_energy, self.energy + amount)

    def update(self, dt: float):
        if self.state_timer > 0:
            self.state_timer -= 1
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.combo_timer > 0:
            self.combo_timer -= 1

        self.stamina = min(self.max_stamina, self.stamina + STAMINA_REGEN * dt)

        if not self.on_ground:
            self.vy -= GRAVITY * dt
            self.y += self.vy * dt
            if self.y <= GROUND_Y:
                self.y = GROUND_Y
                self.vy = 0.0
                self.on_ground = True
                self.jump_count = 0

        self.x += self.vx * dt
        self.x = max(ARENA_LEFT, min(ARENA_RIGHT, self.x))

    def set_state(self, new_state: FighterState, duration: int = 0):
        self.state = new_state
        self.state_timer = duration
        self.attack_hit = False
```

- [ ] **Step 3: Verify by importing the module**

Run: `cd /workspace && python -c "from kivy_app.game.fighter import Fighter, FighterState; f = Fighter(1, 100, 156); f.take_damage(10); assert f.hp == 90; print('OK')"`
Expected: prints "OK"

- [ ] **Step 4: Commit**

```bash
git add kivy_app/game/__init__.py kivy_app/game/fighter.py
git commit -m "feat: add Fighter data model with state machine and physics"
```

---

### Task 2: Combat system (hitbox, damage, combo)

**Files:**
- Create: `/workspace/kivy_app/game/combat.py`

- [ ] **Step 1: Write CombatSystem**

```python
# /workspace/kivy_app/game/combat.py
from dataclasses import dataclass
from .fighter import Fighter, FighterState


@dataclass
class Hitbox:
    x: float
    y: float
    w: float
    h: float

    def intersects(self, other: "Hitbox") -> bool:
        return (
            self.x < other.x + other.w
            and self.x + self.w > other.x
            and self.y < other.y + other.h
            and self.y + self.h > other.y
        )


LIGHT_DAMAGE = 5
HEAVY_DAMAGE = 12
SPECIAL_DAMAGE = 25
COMBO_BONUS = 3
COMBO_WINDOW = 18
LIGHT_DURATION = 8
HEAVY_DURATION = 14
SPECIAL_DURATION = 30


def get_attack_hitbox(f: Fighter) -> Hitbox:
    range_offset = 24 if f.facing_right else -24
    return Hitbox(
        x=f.x + range_offset,
        y=f.y + 4,
        w=20,
        h=16,
    )


def get_body_hitbox(f: Fighter) -> Hitbox:
    return Hitbox(x=f.x - 8, y=f.y - 12, w=16, h=28)


def calculate_damage(
    attack_type: str, is_guarding: bool, combo_count: int
) -> int:
    base = {
        "light": LIGHT_DAMAGE,
        "heavy": HEAVY_DAMAGE,
        "special": SPECIAL_DAMAGE,
    }.get(attack_type, 0)

    if attack_type == "special":
        return base

    if is_guarding:
        base = max(1, base // 5)

    if combo_count >= 3 and attack_type == "light":
        base += COMBO_BONUS

    return base


class CombatSystem:
    def __init__(self):
        self._hit_this_attack: dict[int, bool] = {}

    def check_hit(self, attacker: Fighter, defender: Fighter) -> int:
        attack_type = None
        if attacker.state == FighterState.LIGHT_ATTACK and not attacker.attack_hit:
            attack_type = "light"
        elif attacker.state == FighterState.HEAVY_ATTACK and not attacker.attack_hit:
            attack_type = "heavy"
        elif attacker.state == FighterState.SPECIAL and not attacker.attack_hit:
            attack_type = "special"

        if attack_type is None:
            return 0

        a_hitbox = get_attack_hitbox(attacker)
        d_hitbox = get_body_hitbox(defender)

        if not a_hitbox.intersects(d_hitbox):
            return 0

        attacker.attack_hit = True

        is_guarding = defender.state == FighterState.GUARD
        damage = calculate_damage(attack_type, is_guarding, attacker.combo_count)
        defender.take_damage(damage)

        if attack_type == "light":
            attacker.combo_count += 1
            attacker.combo_timer = COMBO_WINDOW
        elif not is_guarding:
            attacker.add_energy(10)

        attacker.add_energy(10)

        return damage

    def update_combo(self, attacker: Fighter):
        if attacker.combo_timer <= 0:
            attacker.combo_count = 0
```

- [ ] **Step 2: Verify combat logic**

Run: `cd /workspace && python -c "
from kivy_app.game.fighter import Fighter, FighterState
from kivy_app.game.combat import calculate_damage, Hitbox, get_attack_hitbox, get_body_hitbox
assert calculate_damage('light', False, 0) == 5
assert calculate_damage('heavy', False, 0) == 12
assert calculate_damage('light', True, 0) == 1
assert calculate_damage('light', False, 3) == 8
assert calculate_damage('special', True, 0) == 25
h1 = Hitbox(0, 0, 10, 10)
h2 = Hitbox(5, 5, 10, 10)
assert h1.intersects(h2)
h3 = Hitbox(20, 20, 10, 10)
assert not h1.intersects(h3)
print('OK')
"`
Expected: prints "OK"

- [ ] **Step 3: Commit**

```bash
git add kivy_app/game/combat.py
git commit -m "feat: add CombatSystem with hitbox detection, damage calc, and combo logic"
```

---

### Task 3: Input controls (virtual stick + action buttons)

**Files:**
- Create: `/workspace/kivy_app/game/controls.py`

- [ ] **Step 1: Write VirtualStick and ActionButton widgets**

```python
# /workspace/kivy_app/game/controls.py
from dataclasses import dataclass
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
from kivy.properties import NumericProperty, BooleanProperty
from math import sqrt, atan2


@dataclass
class ControlState:
    dx: float = 0.0
    dy: float = 0.0
    jump: bool = False
    light_attack: bool = False
    heavy_attack: bool = False
    guard: bool = False
    dash: bool = False
    special: bool = False


DEAD_ZONE = 0.15


class VirtualStick(Widget):
    stick_x = NumericProperty(0.0)
    stick_y = NumericProperty(0.0)
    radius = NumericProperty(50)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._touch_uid = None
        self._center_x = 0
        self._center_y = 0
        self.bind(pos=self._update_center, size=self._update_center)

    def _update_center(self, *args):
        self._center_x = self.x + self.width / 2
        self._center_y = self.y + self.height / 2
        self.radius = min(self.width, self.height) / 2 - 4

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        if self._touch_uid is not None:
            return False
        self._touch_uid = touch.uid
        self._update_stick(touch)
        return True

    def on_touch_move(self, touch):
        if touch.uid != self._touch_uid:
            return False
        self._update_stick(touch)
        return True

    def on_touch_up(self, touch):
        if touch.uid != self._touch_uid:
            return False
        self._touch_uid = None
        self.stick_x = 0.0
        self.stick_y = 0.0
        return True

    def _update_stick(self, touch):
        dx = touch.x - self._center_x
        dy = touch.y - self._center_y
        dist = sqrt(dx * dx + dy * dy)
        if dist > self.radius:
            scale = self.radius / dist
            dx *= scale
            dy *= scale
            dist = self.radius
        normalized = dist / self.radius if self.radius > 0 else 0
        if normalized < DEAD_ZONE:
            self.stick_x = 0.0
            self.stick_y = 0.0
        else:
            self.stick_x = dx / self.radius
            self.stick_y = dy / self.radius

    def get_direction(self):
        return (self.stick_x, self.stick_y)


class ActionButton(Widget):
    pressed = BooleanProperty(False)
    label = ""

    def __init__(self, label="", **kwargs):
        super().__init__(**kwargs)
        self.label = label

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        self.pressed = True
        return True

    def on_touch_up(self, touch):
        if self.pressed:
            self.pressed = False
            return True
        return False
```

- [ ] **Step 2: Add drawing for VirtualStick and ActionButton**

Add to `VirtualStick` (append to __init__):

```python
    def _draw(self):
        self.canvas.clear()
        with self.canvas:
            Color(0.3, 0.3, 0.3, 0.5)
            Line(circle=(self._center_x, self._center_y, self.radius), width=2)
            Color(0.6, 0.6, 0.6, 0.7)
            sx = self._center_x + self.stick_x * self.radius
            sy = self._center_y + self.stick_y * self.radius
            Ellipse(pos=(sx - 12, sy - 12), size=(24, 24))
```

Modify `_update_stick` to call `self._draw()` at end; modify `__init__` to `self.bind(stick_x=self._on_stick_change, stick_y=self._on_stick_change, pos=self._on_stick_change, size=self._on_stick_change)` where `_on_stick_change` calls `self._draw()`.

Add to `ActionButton` (append to __init__):

```python
    def _draw(self):
        self.canvas.clear()
        with self.canvas:
            c = (0.2, 0.7, 0.2, 0.6) if self.pressed else (0.3, 0.3, 0.3, 0.5)
            Color(*c)
            from kivy.graphics import Rectangle
            Rectangle(pos=self.pos, size=self.size)
```

Bind `pressed` to `_draw` and `pos`/`size` too.

- [ ] **Step 3: Verify controls module imports correctly**

Run: `cd /workspace && python -c "from kivy_app.game.controls import ControlState, VirtualStick, ActionButton; cs = ControlState(dx=0.5, jump=True); assert cs.jump; print('OK')"`
Expected: prints "OK"

- [ ] **Step 4: Commit**

```bash
git add kivy_app/game/controls.py
git commit -m "feat: add VirtualStick and ActionButton input controls"
```

---

### Task 4: Programmatic pixel mecha sprites

**Files:**
- Create: `/workspace/kivy_app/game/sprites.py`

This is the largest module. Each mecha is drawn as geometric primitives (rectangles for head, torso, arms, legs, with eyes/visor). Animation states are defined as pose configurations that determine the position/rotation of each body part.

- [ ] **Step 1: Write the sprite data definitions**

```python
# /workspace/kivy_app/game/sprites.py
from kivy.graphics import Color, Rectangle, PushMatrix, PopMatrix, Rotate, Translate
from kivy.graphics.instructions import InstructionGroup

# Canvas logical size: 320x180, mecha drawn relative to fighter world position
# Each mecha is 24x32 pixels drawn as body parts

BLUE_PALETTE = {
    "body": (0.2, 0.4, 0.9),
    "dark": (0.1, 0.25, 0.7),
    "light": (0.3, 0.6, 1.0),
    "accent": (0.5, 0.8, 1.0),
    "visor": (0.8, 0.95, 1.0),
    "blade": (0.9, 0.95, 1.0),
    "joint": (0.15, 0.3, 0.6),
    "thruster": (0.4, 0.7, 1.0),
}

RED_PALETTE = {
    "body": (0.9, 0.2, 0.15),
    "dark": (0.6, 0.1, 0.1),
    "light": (1.0, 0.4, 0.2),
    "accent": (1.0, 0.6, 0.2),
    "visor": (1.0, 0.9, 0.4),
    "blade": (1.0, 0.5, 0.0),
    "joint": (0.5, 0.15, 0.1),
    "thruster": (1.0, 0.7, 0.3),
}


class MechaPart:
    def __init__(self, name, color_key, x, y, w, h, angle=0):
        self.name = name
        self.color_key = color_key
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.angle = angle


class MechaFrame:
    def __init__(self, parts, offset_y=0):
        self.parts = parts
        self.offset_y = offset_y


class MechaAnimation:
    def __init__(self, frames, fps, loop=True):
        self.frames = frames
        self.fps = fps
        self.loop = loop
        self.frame_duration = 1.0 / fps if fps > 0 else 0.1


def _make_idle_frames(palette):
    frames = []
    for i in range(4):
        bob = [-1, 0, 1, 0][i]
        frames.append(MechaFrame([
            MechaPart("head", "body", 2, 20 + bob, 8, 8),
            MechaPart("visor", "visor", 3, 22 + bob, 6, 3),
            MechaPart("torso", "dark", 3, 12, 6, 9),
            MechaPart("chest", "body", 4, 13, 4, 5),
            MechaPart("l_arm", "body", -3, 12, 5, 8),
            MechaPart("l_hand", "joint", -4, 10, 3, 3),
            MechaPart("r_arm", "body", 10, 13, 5, 8),
            MechaPart("r_hand", "light", 13, 12, 4, 3),
            MechaPart("l_leg", "dark", 1, 2, 5, 11),
            MechaPart("l_foot", "joint", 0, 0, 6, 3),
            MechaPart("r_leg", "dark", 7, 3, 5, 11),
            MechaPart("r_foot", "joint", 6, 0, 6, 3),
            MechaPart("core", "accent", 5, 15, 2, 2),
        ], offset_y=0))
    return frames


def _make_walk_frames(palette):
    frames = []
    for i in range(6):
        leg_offset = [-2, -1, 0, 1, 2, 1][i]
        arm_swing = [1, 0, -1, 0, 1, 0][i]
        bob = [-1, 0, 1, 0, -1, 0][i]
        frames.append(MechaFrame([
            MechaPart("head", "body", 2, 20 + bob, 8, 8),
            MechaPart("visor", "visor", 3, 22 + bob, 6, 3),
            MechaPart("torso", "dark", 3, 12 + bob, 6, 9),
            MechaPart("chest", "body", 4, 13 + bob, 4, 5),
            MechaPart("l_arm", "body", -3 + arm_swing, 12 + bob, 5, 8),
            MechaPart("l_hand", "joint", -4, 10 + arm_swing + bob, 3, 3),
            MechaPart("r_arm", "body", 10 - arm_swing, 13 + bob, 5, 8),
            MechaPart("r_hand", "light", 13, 12 - arm_swing + bob, 4, 3),
            MechaPart("l_leg", "dark", 1 + leg_offset, 2, 5, 11),
            MechaPart("l_foot", "joint", 0 + leg_offset, 0, 6, 3),
            MechaPart("r_leg", "dark", 7 - leg_offset, 3, 5, 11),
            MechaPart("r_foot", "joint", 6 - leg_offset, 0, 6, 3),
            MechaPart("core", "accent", 5, 15 + bob, 2, 2),
        ], offset_y=0))
    return frames


def _make_jump_frames(palette):
    return [
        MechaFrame([
            MechaPart("head", "body", 2, 18, 8, 8),
            MechaPart("visor", "visor", 3, 20, 6, 3),
            MechaPart("torso", "dark", 3, 10, 6, 9),
            MechaPart("chest", "body", 4, 11, 4, 5),
            MechaPart("l_arm", "body", -4, 12, 5, 6),
            MechaPart("r_arm", "body", 11, 12, 5, 6),
            MechaPart("l_hand", "joint", -5, 11, 3, 2),
            MechaPart("r_hand", "light", 14, 11, 3, 2),
            MechaPart("l_leg", "dark", 2, 4, 5, 7),
            MechaPart("l_foot", "joint", 1, 0, 5, 5),
            MechaPart("r_leg", "dark", 6, 4, 5, 7),
            MechaPart("r_foot", "joint", 5, 0, 5, 5),
            MechaPart("core", "accent", 5, 13, 2, 2),
            MechaPart("thruster", "thruster", 3, 0, 6, 2),
        ]),
        MechaFrame([
            MechaPart("head", "body", 2, 19, 8, 8),
            MechaPart("visor", "visor", 3, 21, 6, 3),
            MechaPart("torso", "dark", 3, 11, 6, 9),
            MechaPart("chest", "body", 4, 12, 4, 5),
            MechaPart("l_arm", "body", -3, 13, 5, 5),
            MechaPart("r_arm", "body", 10, 13, 5, 5),
            MechaPart("l_hand", "joint", -4, 12, 3, 2),
            MechaPart("r_hand", "light", 13, 12, 3, 2),
            MechaPart("l_leg", "dark", 2, 5, 5, 7),
            MechaPart("l_foot", "joint", 1, 1, 5, 5),
            MechaPart("r_leg", "dark", 6, 5, 5, 7),
            MechaPart("r_foot", "joint", 5, 1, 5, 5),
            MechaPart("core", "accent", 5, 14, 2, 2),
        ]),
    ]


def _make_dash_frames(palette):
    frames = []
    for i in range(4):
        lean = [2, 4, 6, 4][i]
        alpha = [0.7, 0.5, 0.3, 0.5][i]
        frames.append(MechaFrame([
            MechaPart("head", "body", 2 + lean, 19, 8, 8),
            MechaPart("visor", "visor", 3 + lean, 21, 6, 3),
            MechaPart("torso", "dark", 3, 11, 8, 9),
            MechaPart("chest", "body", 4, 12, 6, 5),
            MechaPart("l_arm", "body", 2, 11, 4, 8),
            MechaPart("r_arm", "body", 11, 13, 6, 7),
            MechaPart("l_hand", "joint", 1, 10, 3, 3),
            MechaPart("r_hand", "light", 14, 14, 3, 3),
            MechaPart("l_leg", "dark", 2 + lean // 2, 2, 5, 10),
            MechaPart("r_leg", "dark", 7 + lean // 2, 3, 5, 10),
            MechaPart("l_foot", "joint", 1 + lean // 2, 0, 5, 3),
            MechaPart("r_foot", "joint", 6 + lean // 2, 0, 5, 3),
            MechaPart("core", "accent", 5 + lean // 2, 14, 2, 2),
        ], offset_y=0))
    return frames


def _make_light_attack_frames(palette):
    frames = []
    for i in range(4):
        ext = [0, 4, 8, 4][i]
        frames.append(MechaFrame([
            MechaPart("head", "body", 2, 20, 8, 8),
            MechaPart("visor", "visor", 3, 22, 6, 3),
            MechaPart("torso", "dark", 3, 12, 6, 9),
            MechaPart("chest", "body", 4, 13, 4, 5),
            MechaPart("l_arm", "body", -2, 12, 4, 7),
            MechaPart("r_arm", "body", 10 + ext, 13, 5, 7),
            MechaPart("r_hand", "light", 13 + ext, 14, 4, 3),
            MechaPart("l_hand", "joint", -3, 11, 3, 2),
            MechaPart("l_leg", "dark", 1, 2, 5, 11),
            MechaPart("r_leg", "dark", 7, 3, 5, 11),
            MechaPart("l_foot", "joint", 0, 0, 6, 3),
            MechaPart("r_foot", "joint", 6, 0, 6, 3),
            MechaPart("core", "accent", 5, 15, 2, 2),
            MechaPart("blade", "blade", 14 + ext, 14, 6, 2),
        ], offset_y=0))
    return frames


def _make_heavy_attack_frames(palette):
    frames = []
    for i in range(6):
        if i < 2:
            windup = -3 - i * 2
            ext = 0
        elif i < 4:
            ext = [4, 10][i - 2]
            windup = 0
        else:
            ext = 4
            windup = 0
        frames.append(MechaFrame([
            MechaPart("head", "body", 2 + windup, 20, 8, 8),
            MechaPart("visor", "visor", 3 + windup, 22, 6, 3),
            MechaPart("torso", "dark", 3, 12, 6, 9),
            MechaPart("chest", "body", 4, 13, 4, 5),
            MechaPart("l_arm", "body", -2 + windup, 12, 4, 7),
            MechaPart("r_arm", "body", 8, 12 + windup, 7, 7),
            MechaPart("r_hand", "light", 10 + ext, 12 - windup, 5, 4),
            MechaPart("l_hand", "joint", -3, 11, 3, 2),
            MechaPart("l_leg", "dark", 1, 2, 5, 11),
            MechaPart("r_leg", "dark", 7, 3, 5, 11),
            MechaPart("l_foot", "joint", 0, 0, 6, 3),
            MechaPart("r_foot", "joint", 6, 0, 6, 3),
            MechaPart("core", "accent", 5, 15, 2, 2),
        ], offset_y=0))
    return frames


def _make_guard_frames(palette):
    return [
        MechaFrame([
            MechaPart("head", "body", 1, 18, 8, 8),
            MechaPart("visor", "visor", 2, 20, 6, 3),
            MechaPart("torso", "dark", 3, 11, 6, 8),
            MechaPart("chest", "body", 4, 12, 4, 4),
            MechaPart("l_arm", "body", 0, 15, 5, 5),
            MechaPart("r_arm", "body", 7, 15, 5, 5),
            MechaPart("l_hand", "joint", -1, 14, 6, 3),
            MechaPart("r_hand", "light", 7, 14, 6, 3),
            MechaPart("l_leg", "dark", 1, 2, 5, 11),
            MechaPart("r_leg", "dark", 7, 3, 5, 11),
            MechaPart("l_foot", "joint", 0, 0, 6, 3),
            MechaPart("r_foot", "joint", 6, 0, 6, 3),
            MechaPart("core", "accent", 5, 14, 2, 2),
            MechaPart("shield", "accent", -1, 8, 14, 8),
        ]),
        MechaFrame([
            MechaPart("head", "body", 1, 18, 8, 8),
            MechaPart("visor", "visor", 2, 20, 6, 3),
            MechaPart("torso", "dark", 3, 11, 6, 8),
            MechaPart("chest", "body", 4, 12, 4, 4),
            MechaPart("l_arm", "body", 0, 15, 5, 5),
            MechaPart("r_arm", "body", 7, 15, 5, 5),
            MechaPart("l_hand", "joint", -1, 14, 6, 3),
            MechaPart("r_hand", "light", 7, 14, 6, 3),
            MechaPart("l_leg", "dark", 1, 2, 5, 11),
            MechaPart("r_leg", "dark", 7, 3, 5, 11),
            MechaPart("l_foot", "joint", 0, 0, 6, 3),
            MechaPart("r_foot", "joint", 6, 0, 6, 3),
            MechaPart("core", "accent", 5, 14, 2, 2),
            MechaPart("shield", "accent", 0, 9, 12, 6),
        ]),
    ]


def _make_hurt_frames(palette):
    return [
        MechaFrame([
            MechaPart("head", "body", 2, 19, 7, 7),
            MechaPart("visor", "visor", 3, 21, 5, 2),
            MechaPart("torso", "dark", 4, 12, 5, 8),
            MechaPart("chest", "body", 5, 13, 3, 4),
            MechaPart("l_arm", "body", -1, 13, 4, 6),
            MechaPart("r_arm", "body", 10, 14, 4, 5),
            MechaPart("l_leg", "dark", 2, 3, 4, 10),
            MechaPart("r_leg", "dark", 7, 2, 4, 11),
            MechaPart("l_foot", "joint", 1, 0, 6, 3),
            MechaPart("r_foot", "joint", 6, 0, 6, 3),
            MechaPart("core", "accent", 5, 14, 2, 2),
        ]),
        MechaFrame([
            MechaPart("head", "body", 2, 20, 8, 8),
            MechaPart("visor", "visor", 3, 22, 6, 3),
            MechaPart("torso", "dark", 3, 12, 6, 9),
            MechaPart("chest", "body", 4, 13, 4, 5),
            MechaPart("l_arm", "body", -3, 12, 5, 8),
            MechaPart("r_arm", "body", 10, 13, 5, 8),
            MechaPart("l_leg", "dark", 1, 2, 5, 11),
            MechaPart("r_leg", "dark", 7, 3, 5, 11),
            MechaPart("l_foot", "joint", 0, 0, 6, 3),
            MechaPart("r_foot", "joint", 6, 0, 6, 3),
            MechaPart("core", "accent", 5, 15, 2, 2),
        ]),
    ]


def _make_special_frames(palette):
    frames = []
    for i in range(8):
        charge = i if i < 4 else 7 - i
        glow = i % 2 == 0
        frames.append(MechaFrame([
            MechaPart("head", "body", 2, 20, 8, 8),
            MechaPart("visor", "visor", 3, 22, 6, 3),
            MechaPart("torso", "dark", 3, 12, 6, 9),
            MechaPart("chest", "body", 4, 13, 4, 5),
            MechaPart("l_arm", "body", -4, 10, 5, 8),
            MechaPart("r_arm", "body", 11, 10, 5, 8),
            MechaPart("l_hand", "joint", -5, 9, 4, 3),
            MechaPart("r_hand", "light", 14, 9, 4, 3),
            MechaPart("l_leg", "dark", 1, 2, 5, 11),
            MechaPart("r_leg", "dark", 7, 3, 5, 11),
            MechaPart("l_foot", "joint", 0, 0, 6, 3),
            MechaPart("r_foot", "joint", 6, 0, 6, 3),
            MechaPart("core", "accent" if not glow else "visor", 5, 15, 2, 2),
            MechaPart("aura", "thruster", -2 - charge, -2, 16 + charge * 2, 34 + charge * 2),
        ], offset_y=0))
    return frames


ANIMATION_DEFS = {
    "idle": _make_idle_frames,
    "walk": _make_walk_frames,
    "jump": _make_jump_frames,
    "dash": _make_dash_frames,
    "light_attack": _make_light_attack_frames,
    "heavy_attack": _make_heavy_attack_frames,
    "guard": _make_guard_frames,
    "hurt": _make_hurt_frames,
    "special": _make_special_frames,
}

ANIM_FPS = {
    "idle": 6,
    "walk": 10,
    "jump": 4,
    "dash": 12,
    "light_attack": 12,
    "heavy_attack": 10,
    "guard": 0,
    "hurt": 0,
    "special": 12,
}


class SpriteAnimator:
    def __init__(self):
        self._cache: dict[tuple, list[MechaAnimation]] = {}

    def get_animation(self, palette_name, state_name):
        key = (palette_name, state_name)
        if key in self._cache:
            return self._cache[key]

        palette = BLUE_PALETTE if palette_name == "blue" else RED_PALETTE
        frame_func = ANIMATION_DEFS.get(state_name)
        if frame_func is None:
            frame_func = ANIMATION_DEFS["idle"]

        frames = frame_func(palette)
        fps = ANIM_FPS.get(state_name, 8)
        anim = MechaAnimation(frames, fps, state_name != "hurt" and state_name != "guard")
        self._cache[key] = [anim]
        return anim


SPRITE_SCALE = 3


def draw_mecha(canvas, palette_name, state_name, frame_index, x, y, facing_right, scale=SPRITE_SCALE):
    animator = SpriteAnimator()
    anim = animator.get_animation(palette_name, state_name)
    frame = anim.frames[frame_index % len(anim.frames)]
    palette = BLUE_PALETTE if palette_name == "blue" else RED_PALETTE

    cx = x
    cy = y

    if not facing_right:
        flip_factor = -1
        cx += 12 * scale
    else:
        flip_factor = 1

    with canvas:
        PushMatrix()
        Translate(cx, cy)
        if not facing_right:
            from kivy.graphics import Scale
            Scale(-1, 1, 1)

        for part in frame.parts:
            if part.color_key not in palette:
                continue
            r, g, b = palette[part.color_key]
            Color(r, g, b)
            Rectangle(
                pos=(part.x * scale, (part.y + frame.offset_y) * scale),
                size=(part.w * scale, part.h * scale),
            )

        PopMatrix()
```

- [ ] **Step 2: Verify sprites module imports**

Run: `cd /workspace && python -c "from kivy_app.game.sprites import SpriteAnimator, BLUE_PALETTE, RED_PALETTE; a = SpriteAnimator(); anim = a.get_animation('blue', 'idle'); print(f'idle frames: {len(anim.frames)}'); anim2 = a.get_animation('red', 'light_attack'); print(f'light_attack frames: {len(anim2.frames)}'); print('OK')"`
Expected: prints "OK" with frame counts

- [ ] **Step 3: Commit**

```bash
git add kivy_app/game/sprites.py
git commit -m "feat: add programmatic pixel mecha sprite renderer with 9 animation states"
```

---

### Task 5: Scene background and particle effects

**Files:**
- Create: `/workspace/kivy_app/game/scene.py`

- [ ] **Step 1: Write scene renderer**

```python
# /workspace/kivy_app/game/scene.py
import random
from kivy.graphics import Color, Rectangle, Ellipse, Line


GAME_W = 320
GAME_H = 180
GROUND_Y = 156

BUILDING_DATA = [
    {"x": 10, "w": 40, "h": 60, "color": (0.08, 0.06, 0.08)},
    {"x": 55, "w": 25, "h": 80, "color": (0.1, 0.08, 0.1)},
    {"x": 85, "w": 50, "h": 45, "color": (0.06, 0.05, 0.07)},
    {"x": 150, "w": 30, "h": 70, "color": (0.09, 0.07, 0.09)},
    {"x": 200, "w": 50, "h": 55, "color": (0.07, 0.06, 0.08)},
    {"x": 260, "w": 35, "h": 75, "color": (0.1, 0.08, 0.1)},
    {"x": 300, "w": 20, "h": 50, "color": (0.08, 0.07, 0.09)},
]

FAR_BUILDING_DATA = [
    {"x": 5, "w": 60, "h": 100, "color": (0.04, 0.02, 0.06)},
    {"x": 120, "w": 70, "h": 120, "color": (0.03, 0.02, 0.05)},
    {"x": 240, "w": 55, "h": 90, "color": (0.04, 0.03, 0.06)},
]


class Particle:
    def __init__(self, x, y, vx, vy, life, color, size=2):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.alive = True

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy -= 60 * dt
        self.life -= dt
        if self.life <= 0:
            self.alive = False


class SceneRenderer:
    def __init__(self):
        self.particles: list[Particle] = []

    def spawn_hit_particles(self, x, y):
        for _ in range(6):
            vx = random.uniform(-80, 80)
            vy = random.uniform(40, 120)
            color = (1.0, 0.8, 0.2)
            self.particles.append(Particle(x, y, vx, vy, 0.4, color, 3))

    def spawn_special_particles(self, x, y):
        for _ in range(20):
            vx = random.uniform(-150, 150)
            vy = random.uniform(-50, 200)
            color = (
                random.uniform(0.5, 1.0),
                random.uniform(0.5, 1.0),
                random.uniform(0.8, 1.0),
            )
            self.particles.append(Particle(x, y, vx, vy, 0.8, color, random.randint(2, 5)))

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]
        if len(self.particles) > 50:
            self.particles = self.particles[-50:]

    def draw_background(self, canvas):
        with canvas:
            Color(0.06, 0.02, 0.1)
            Rectangle(pos=(0, 0), size=(GAME_W, GAME_H))

            Color(0.08, 0.03, 0.12)
            Rectangle(pos=(0, 40), size=(GAME_W, 60))

            Color(0.1, 0.05, 0.08)
            Rectangle(pos=(0, 100), size=(GAME_W, 56))

            for b in FAR_BUILDING_DATA:
                Color(*b["color"])
                Rectangle(pos=(b["x"], GROUND_Y - b["h"]), size=(b["w"], b["h"]))

            Color(0.12, 0.08, 0.1)
            for x in range(0, GAME_W, 8):
                for y in range(GROUND_Y - 20, GROUND_Y, 6):
                    if (x // 8 + y // 6) % 3 == 0:
                        Rectangle(pos=(x, y), size=(3, 3))

            for b in BUILDING_DATA:
                Color(*b["color"])
                Rectangle(pos=(b["x"], GROUND_Y - b["h"]), size=(b["w"], b["h"]))
                window_w = 5
                window_h = 6
                for wx in range(b["x"] + 5, b["x"] + b["w"] - 5, 8):
                    for wy in range(GROUND_Y - b["h"] + 8, GROUND_Y - 10, 10):
                        Color(0.3, 0.25, 0.05)
                        Rectangle(pos=(wx, wy), size=(window_w, window_h))

            Color(0.15, 0.1, 0.05)
            Rectangle(pos=(0, GROUND_Y - 4), size=(GAME_W, 4))
            Color(0.2, 0.15, 0.08)
            Rectangle(pos=(0, GROUND_Y), size=(GAME_W, 24))

    def draw_particles(self, canvas):
        with canvas:
            for p in self.particles:
                alpha = p.life / p.max_life
                Color(p.color[0], p.color[1], p.color[2], alpha)
                Rectangle(
                    pos=(p.x - p.size / 2, p.y - p.size / 2),
                    size=(p.size, p.size),
                )
```

- [ ] **Step 2: Verify scene module imports**

Run: `cd /workspace && python -c "from kivy_app.game.scene import SceneRenderer, Particle, GAME_W, GAME_H, GROUND_Y; sr = SceneRenderer(); sr.spawn_hit_particles(160, 100); assert len(sr.particles) == 6; sr.update(0.016); print('OK')"`
Expected: prints "OK"

- [ ] **Step 3: Commit**

```bash
git add kivy_app/game/scene.py
git commit -m "feat: add city ruins background and particle effects system"
```

---

### Task 6: HUD overlay (health bars, energy, combo counter, win screen)

**Files:**
- Create: `/workspace/kivy_app/game/ui.py`

- [ ] **Step 1: Write HUD renderer**

```python
# /workspace/kivy_app/game/ui.py
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.label import Label

GAME_W = 320
GAME_H = 180

BAR_W = 100
BAR_H = 6
BAR_Y = 172
ENERGY_BAR_H = 3
STAMINA_BAR_H = 3
P1_HP_X = 8
P1_ENERGY_X = 8
P1_STAMINA_X = 8
P2_HP_X = 212
P2_ENERGY_X = 212
P2_STAMINA_X = 212


def draw_hud(canvas, f1, f2):
    hud_y_hp = BAR_Y
    hud_y_energy = BAR_Y - 5
    hud_y_stamina = BAR_Y - 9

    with canvas:
        Color(0.1, 0.1, 0.1, 0.7)
        Rectangle(pos=(2, BAR_Y - 12), size=(GAME_W - 4, 18))

        Color(0.3, 0.3, 0.3)
        Rectangle(pos=(P1_HP_X, hud_y_hp), size=(BAR_W, BAR_H))
        Rectangle(pos=(P2_HP_X, hud_y_hp), size=(BAR_W, BAR_H))

        hp1_ratio = f1.hp / f1.max_hp
        hp1_w = max(0, int(BAR_W * hp1_ratio))
        if hp1_ratio > 0.5:
            Color(0.2, 0.5, 1.0)
        elif hp1_ratio > 0.25:
            Color(1.0, 0.8, 0.2)
        else:
            Color(1.0, 0.2, 0.2)
        Rectangle(pos=(P1_HP_X, hud_y_hp), size=(hp1_w, BAR_H))

        hp2_ratio = f2.hp / f2.max_hp
        hp2_w = max(0, int(BAR_W * hp2_ratio))
        if hp2_ratio > 0.5:
            Color(0.2, 0.5, 1.0)
        elif hp2_ratio > 0.25:
            Color(1.0, 0.8, 0.2)
        else:
            Color(1.0, 0.2, 0.2)
        Rectangle(pos=(P2_HP_X, hud_y_hp), size=(hp2_w, BAR_H))

        Color(0.2, 0.2, 0.2)
        Rectangle(pos=(P1_ENERGY_X, hud_y_energy), size=(BAR_W, ENERGY_BAR_H))
        Rectangle(pos=(P2_ENERGY_X, hud_y_energy), size=(BAR_W, ENERGY_BAR_H))

        e1_ratio = f1.energy / f1.max_energy
        e1_w = max(0, int(BAR_W * e1_ratio))
        Color(1.0, 0.8, 0.2) if e1_ratio >= 1.0 else Color(0.3, 0.3, 0.8)
        Rectangle(pos=(P1_ENERGY_X, hud_y_energy), size=(e1_w, ENERGY_BAR_H))

        e2_ratio = f2.energy / f2.max_energy
        e2_w = max(0, int(BAR_W * e2_ratio))
        Color(1.0, 0.8, 0.2) if e2_ratio >= 1.0 else Color(0.3, 0.3, 0.8)
        Rectangle(pos=(P2_ENERGY_X, hud_y_energy), size=(e2_w, ENERGY_BAR_H))

        Color(0.2, 0.2, 0.2)
        Rectangle(pos=(P1_STAMINA_X, hud_y_stamina), size=(BAR_W, STAMINA_BAR_H))
        Rectangle(pos=(P2_STAMINA_X, hud_y_stamina), size=(BAR_W, STAMINA_BAR_H))

        s1_ratio = f1.stamina / f1.max_stamina
        s1_w = max(0, int(BAR_W * s1_ratio))
        Color(0.6, 0.6, 0.6) if s1_ratio > 0.2 else Color(1.0, 0.5, 0.5)
        Rectangle(pos=(P1_STAMINA_X, hud_y_stamina), size=(s1_w, STAMINA_BAR_H))

        s2_ratio = f2.stamina / f2.max_stamina
        s2_w = max(0, int(BAR_W * s2_ratio))
        Color(0.6, 0.6, 0.6) if s2_ratio > 0.2 else Color(1.0, 0.5, 0.5)
        Rectangle(pos=(P2_STAMINA_X, hud_y_stamina), size=(s2_w, STAMINA_BAR_H))


def draw_combo(canvas, fighter, x, y):
    if fighter.combo_count < 2:
        return
    from kivy.graphics import Color as KColor, Rectangle

    combo_str = str(fighter.combo_count)
    char_w = 4
    char_h = 6
    start_x = x - (len(combo_str) * char_w) // 2

    with canvas:
        KColor(1.0, 0.8, 0.2)
        for i, ch in enumerate(combo_str):
            px = start_x + i * char_w
            for py_offset in range(char_h):
                for px_offset in range(char_w):
                    if _char_pixel(ch, px_offset, py_offset):
                        Rectangle(
                            pos=(px + px_offset, y + char_h - py_offset),
                            size=(1, 1),
                        )


def _char_pixel(ch, x, y):
    font = {
        "0": [(1,0),(2,0),(0,1),(3,1),(0,2),(3,2),(0,3),(3,3),(0,4),(3,4),(1,5),(2,5)],
        "1": [(2,0),(1,1),(2,1),(2,2),(2,3),(2,4),(1,5),(2,5),(3,5)],
        "2": [(1,0),(2,0),(3,0),(3,1),(3,2),(1,2),(2,2),(0,3),(0,4),(0,5),(1,5),(2,5),(3,5)],
        "3": [(1,0),(2,0),(3,0),(3,1),(2,2),(3,2),(3,3),(1,4),(2,4),(3,4)],
        "4": [(0,0),(3,0),(0,1),(3,1),(0,2),(1,2),(2,2),(3,2),(3,3),(3,4)],
        "5": [(0,0),(1,0),(2,0),(3,0),(0,1),(0,2),(1,2),(2,2),(3,2),(3,3),(0,4),(1,4),(2,4),(3,4)],
        "6": [(1,0),(2,0),(3,0),(0,1),(0,2),(1,2),(2,2),(0,3),(3,3),(0,4),(3,4),(1,5),(2,5)],
        "7": [(0,0),(1,0),(2,0),(3,0),(3,1),(2,2),(2,3),(1,4)],
        "8": [(1,0),(2,0),(0,1),(3,1),(1,2),(2,2),(0,3),(3,3),(0,4),(3,4),(1,5),(2,5)],
        "9": [(1,0),(2,0),(0,1),(3,1),(0,2),(3,2),(1,3),(2,3),(3,3),(3,4),(1,5),(2,5)],
    }
    pixels = font.get(ch, [])
    return (x, y) in pixels


def draw_win_screen(canvas, winner_id):
    with canvas:
        Color(0, 0, 0, 0.7)
        Rectangle(pos=(0, 0), size=(GAME_W, GAME_H))

        # win text drawn by engine with Kivy Labels
```

- [ ] **Step 2: Verify HUD module imports**

Run: `cd /workspace && python -c "from kivy_app.game.ui import draw_hud; print('OK')"`
Expected: prints "OK"

- [ ] **Step 3: Commit**

```bash
git add kivy_app/game/ui.py
git commit -m "feat: add HUD system with HP/energy/stamina bars and combo display"
```

---

### Task 7: Game engine (main loop, state machine, orchestration)

**Files:**
- Create: `/workspace/kivy_app/game/engine.py`

This is the core orchestrator. It creates fighters, controls, handles the game loop, coordinates combat, and manages game state transitions.

- [ ] **Step 1: Write GameWidget**

```python
# /workspace/kivy_app/game/engine.py
from enum import Enum, auto
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, PushMatrix, PopMatrix, Translate, Scale, ClearColor, ClearBuffers
from kivy.core.window import Window
from kivy.properties import NumericProperty

from .fighter import (
    Fighter,
    FighterState,
    GROUND_Y,
    MOVE_SPEED,
    JUMP_VELOCITY,
    DASH_SPEED,
    DASH_DURATION,
    STAMINA_DASH_COST,
    STAMINA_GUARD_COST,
)
from .combat import CombatSystem, LIGHT_DURATION, HEAVY_DURATION, SPECIAL_DURATION
from .controls import ControlState, VirtualStick, ActionButton
from .sprites import draw_mecha
from .scene import SceneRenderer
from .ui import draw_hud, draw_combo

GAME_W = 320
GAME_H = 180
SCREEN_W = 960
SCREEN_H = 540
SCALE_X = SCREEN_W / GAME_W
SCALE_Y = SCREEN_H / GAME_H


class GameState(Enum):
    IDLE = auto()
    COUNTDOWN = auto()
    FIGHTING = auto()
    WINNER = auto()


class GameWidget(Widget):
    game_state = "idle"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (SCREEN_W, SCREEN_H)
        Window.size = (SCREEN_W + 1, SCREEN_H + 1)

        self._game_state = GameState.IDLE
        self._countdown_timer = 3.0
        self._winner_timer = 3.0
        self._winner_id = 0

        self.fighters = [
            Fighter(player_id=1, x=80, y=GROUND_Y, facing_right=True),
            Fighter(player_id=2, x=240, y=GROUND_Y, facing_right=False),
        ]

        self.combat = CombatSystem()
        self.scene = SceneRenderer()

        self._p1_controls = ControlState()
        self._p2_controls = ControlState()
        self._p1_last_jump = False
        self._p2_last_jump = False
        self._p1_last_light = False
        self._p2_last_light = False
        self._p1_last_heavy = False
        self._p2_last_heavy = False
        self._p1_last_special = False
        self._p2_last_special = False
        self._p1_last_dash = False
        self._p2_last_dash = False

        self._frame = 0
        self._sprite_frame = {1: 0, 2: 0}
        self._sprite_timer = {1: 0.0, 2: 0.0}
        self._anim_fps = {
            FighterState.IDLE: 6,
            FighterState.WALK: 10,
            FighterState.JUMP: 4,
            FighterState.DASH: 12,
            FighterState.LIGHT_ATTACK: 12,
            FighterState.HEAVY_ATTACK: 10,
            FighterState.GUARD: 0,
            FighterState.HURT: 8,
            FighterState.SPECIAL: 12,
        }

        self._build_ui()
        Clock.schedule_interval(self._update, 1.0 / 60.0)

    def _build_ui(self):
        pass

    def set_controls(self, p1: ControlState, p2: ControlState):
        self._p1_controls = p1
        self._p2_controls = p2

    def _update(self, dt):
        self._frame += 1

        f1, f2 = self.fighters

        if self._game_state == GameState.IDLE:
            pass
        elif self._game_state == GameState.COUNTDOWN:
            self._countdown_timer -= dt
            if self._countdown_timer <= 0:
                self._game_state = GameState.FIGHTING
        elif self._game_state == GameState.FIGHTING:
            self._process_input(f1, self._p1_controls, f2)
            self._process_input(f2, self._p2_controls, f1)

            if f1.state != FighterState.HURT and f1.state != FighterState.SPECIAL:
                f2.facing_right = f1.x < f2.x
            if f2.state != FighterState.HURT and f2.state != FighterState.SPECIAL:
                f1.facing_right = f2.x > f1.x

            f1.update(dt)
            f2.update(dt)

            self.combat.check_hit(f1, f2)
            self.combat.check_hit(f2, f1)

            self.combat.update_combo(f1)
            self.combat.update_combo(f2)

            if f1.hp <= 0:
                self._game_state = GameState.WINNER
                self._winner_id = 2
                self._winner_timer = 3.0
            elif f2.hp <= 0:
                self._game_state = GameState.WINNER
                self._winner_id = 1
                self._winner_timer = 3.0

        elif self._game_state == GameState.WINNER:
            self._winner_timer -= dt
            if self._winner_timer <= 0:
                self._reset_game()

        self.scene.update(dt)

        self._update_sprite_animations(dt)

        self._render()

    def _process_input(self, f: Fighter, ctrl: ControlState, opponent: Fighter):
        if f.state in (FighterState.HURT, FighterState.SPECIAL):
            if f.state_timer <= 0 and f.state == FighterState.HURT:
                f.set_state(FighterState.IDLE)
            elif f.state_timer <= 0 and f.state == FighterState.SPECIAL:
                f.set_state(FighterState.IDLE)
            return

        attacking = f.state in (
            FighterState.LIGHT_ATTACK,
            FighterState.HEAVY_ATTACK,
        )
        if attacking and f.state_timer > 0:
            return

        if f.state == FighterState.DASH and f.state_timer > 0:
            return

        if f.state == FighterState.GUARD:
            if not ctrl.guard:
                f.set_state(FighterState.IDLE)
            else:
                pass
            return

        if ctrl.guard and f.on_ground:
            f.set_state(FighterState.GUARD)
            return

        if ctrl.special and f.energy >= f.max_energy:
            f.energy = 0
            f.set_state(FighterState.SPECIAL, SPECIAL_DURATION)
            self.scene.spawn_special_particles(f.x, f.y + 10)
            return

        if ctrl.dash and f.on_ground and f.spend_stamina(STAMINA_DASH_COST):
            f.vx = DASH_SPEED if f.facing_right else -DASH_SPEED
            f.set_state(FighterState.DASH, DASH_DURATION)
            return

        if ctrl.light_attack and not attacking:
            f.vx = 0
            f.set_state(FighterState.LIGHT_ATTACK, LIGHT_DURATION)
            return

        if ctrl.heavy_attack and not attacking:
            f.vx = 0
            f.set_state(FighterState.HEAVY_ATTACK, HEAVY_DURATION)
            return

        if ctrl.jump:
            if f.on_ground:
                f.vy = JUMP_VELOCITY
                f.on_ground = False
                f.set_state(FighterState.JUMP)
            elif f.jump_count < 1 and f.vy < 100:
                f.vy = JUMP_VELOCITY * 0.8
                f.jump_count += 1
                f.set_state(FighterState.JUMP)

        dx = ctrl.dx
        if dx != 0 and not attacking and f.state != FighterState.DASH:
            f.vx = dx * MOVE_SPEED
            if f.on_ground:
                f.set_state(FighterState.WALK)
        elif f.on_ground and f.state not in (
            FighterState.LIGHT_ATTACK,
            FighterState.HEAVY_ATTACK,
            FighterState.DASH,
        ):
            f.vx = 0
            if f.state_timer <= 0 or f.state == FighterState.WALK:
                f.set_state(FighterState.IDLE)

        if f.state == FighterState.DASH and f.state_timer <= 0:
            f.vx = 0
            f.set_state(FighterState.IDLE)

    def _update_sprite_animations(self, dt):
        for f in self.fighters:
            fps = self._anim_fps.get(f.state, 8)
            if fps == 0:
                self._sprite_timer[f.player_id] = 0
                continue
            self._sprite_timer[f.player_id] += dt
            frame_duration = 1.0 / fps
            while self._sprite_timer[f.player_id] >= frame_duration:
                self._sprite_timer[f.player_id] -= frame_duration
                self._sprite_frame[f.player_id] += 1

    def _render(self):
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1, 1)
            PushMatrix()
            Scale(SCALE_X, SCALE_Y, 1)

            self.scene.draw_background(self.canvas)

            for f in self.fighters:
                palette = "blue" if f.player_id == 1 else "red"
                state_name = f.state.name.lower()
                frame_idx = self._sprite_frame[f.player_id]
                draw_mecha(
                    self.canvas, palette, state_name, frame_idx,
                    f.x - 12, f.y, f.facing_right,
                )

            self.scene.draw_particles(self.canvas)

            f1, f2 = self.fighters
            draw_hud(self.canvas, f1, f2)
            if f1.combo_count >= 2:
                draw_combo(self.canvas, f1, f1.x, f1.y + 40)
            if f2.combo_count >= 2:
                draw_combo(self.canvas, f2, f2.x, f2.y + 40)

            PopMatrix()

    def _reset_game(self):
        self.fighters = [
            Fighter(player_id=1, x=80, y=GROUND_Y, facing_right=True),
            Fighter(player_id=2, x=240, y=GROUND_Y, facing_right=False),
        ]
        self.combat = CombatSystem()
        self.scene = SceneRenderer()
        self._sprite_frame = {1: 0, 2: 0}
        self._sprite_timer = {1: 0.0, 2: 0.0}
        self._game_state = GameState.COUNTDOWN
        self._countdown_timer = 3.0

    def start_game(self):
        self._reset_game()
```

- [ ] **Step 2: Verify engine module imports**

Run: `cd /workspace && python -c "from kivy_app.game.engine import GameWidget, GameState; print('Engine module OK')"`
Expected: prints "Engine module OK"

- [ ] **Step 3: Commit**

```bash
git add kivy_app/game/engine.py
git commit -m "feat: add GameWidget engine with 60fps loop, input processing, and state machine"
```

---

### Task 8: Main entry point with controls layout

**Files:**
- Modify: `/workspace/kivy_app/main.py`

- [ ] **Step 1: Read current main.py** (already read above)

- [ ] **Step 2: Write new main.py**

```python
# /workspace/kivy_app/main.py
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.core.window import Window
from kivy.clock import Clock

from game.engine import GameWidget, GameState, GAME_W, GAME_H, SCREEN_W, SCREEN_H
from game.controls import ControlState, VirtualStick, ActionButton, DEAD_ZONE


class TouchControls(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (SCREEN_W, SCREEN_H)

        self._p1_stick_x = 0.0
        self._p1_stick_y = 0.0
        self._p2_stick_x = 0.0
        self._p2_stick_y = 0.0

        self._p1_stick_touch = None
        self._p2_stick_touch = None

        self._p1_buttons = {
            "jump": False, "light": False, "heavy": False,
            "guard": False, "dash": False, "special": False,
        }
        self._p2_buttons = {
            "jump": False, "light": False, "heavy": False,
            "guard": False, "dash": False, "special": False,
        }

        self._p1_stick_center = (100, 100)
        self._p1_stick_radius = 70
        self._p2_stick_center = (SCREEN_W - 100, 100)
        self._p2_stick_radius = 70

        self._button_radius = 30
        self._p1_button_positions = {}
        self._p2_button_positions = {}

        self._layout_buttons()

    def _layout_buttons(self):
        cx1, cy1 = self._p1_stick_center
        cx2, cy2 = self._p2_stick_center
        br = self._button_radius
        spacing = br * 2 + 16

        self._p1_button_positions = {
            "jump": (cx1 + 130, cy1 + 80),
            "light": (cx1 + 200, cy1 + 80),
            "guard": (cx1 + 130, cy1 - 10),
            "heavy": (cx1 + 200, cy1 - 10),
            "dash": (cx1 + 130, cy1 - 100),
            "special": (cx1 + 200, cy1 - 100),
        }

        self._p2_button_positions = {
            "jump": (cx2 - 200, cy2 + 80),
            "light": (cx2 - 130, cy2 + 80),
            "guard": (cx2 - 200, cy2 - 10),
            "heavy": (cx2 - 130, cy2 - 10),
            "dash": (cx2 - 200, cy2 - 100),
            "special": (cx2 - 130, cy2 - 100),
        }

    def get_controls(self):
        p1 = ControlState(
            dx=self._p1_stick_x,
            dy=self._p1_stick_y,
            jump=self._p1_buttons["jump"],
            light_attack=self._p1_buttons["light"],
            heavy_attack=self._p1_buttons["heavy"],
            guard=self._p1_buttons["guard"],
            dash=self._p1_buttons["dash"],
            special=self._p1_buttons["special"],
        )
        p2 = ControlState(
            dx=self._p2_stick_x,
            dy=self._p2_stick_y,
            jump=self._p2_buttons["jump"],
            light_attack=self._p2_buttons["light"],
            heavy_attack=self._p2_buttons["heavy"],
            guard=self._p2_buttons["guard"],
            dash=self._p2_buttons["dash"],
            special=self._p2_buttons["special"],
        )
        return p1, p2

    def _is_in_stick1(self, x, y):
        cx, cy = self._p1_stick_center
        return (x - cx) ** 2 + (y - cy) ** 2 <= (self._p1_stick_radius * 1.2) ** 2

    def _is_in_stick2(self, x, y):
        cx, cy = self._p2_stick_center
        return (x - cx) ** 2 + (y - cy) ** 2 <= (self._p2_stick_radius * 1.2) ** 2

    def _button_at(self, x, y, positions):
        for name, (bx, by) in positions.items():
            if (x - bx) ** 2 + (y - by) ** 2 <= (self._button_radius * 1.3) ** 2:
                return name
        return None

    def on_touch_down(self, touch):
        if self._is_in_stick1(*touch.pos):
            self._p1_stick_touch = touch.uid
            self._update_stick1(touch)
            return True
        if self._is_in_stick2(*touch.pos):
            self._p2_stick_touch = touch.uid
            self._update_stick2(touch)
            return True

        btn = self._button_at(*touch.pos, self._p1_button_positions)
        if btn:
            self._p1_buttons[btn] = True
            return True

        btn = self._button_at(*touch.pos, self._p2_button_positions)
        if btn:
            self._p2_buttons[btn] = True
            return True

        return False

    def on_touch_move(self, touch):
        if touch.uid == self._p1_stick_touch:
            self._update_stick1(touch)
            return True
        if touch.uid == self._p2_stick_touch:
            self._update_stick2(touch)
            return True
        return False

    def on_touch_up(self, touch):
        if touch.uid == self._p1_stick_touch:
            self._p1_stick_touch = None
            self._p1_stick_x = 0.0
            self._p1_stick_y = 0.0
            return True
        if touch.uid == self._p2_stick_touch:
            self._p2_stick_touch = None
            self._p2_stick_x = 0.0
            self._p2_stick_y = 0.0
            return True

        btn = self._button_at(*touch.pos, self._p1_button_positions)
        if btn:
            self._p1_buttons[btn] = False
            return True

        btn = self._button_at(*touch.pos, self._p2_button_positions)
        if btn:
            self._p2_buttons[btn] = False
            return True

        return False

    def _update_stick1(self, touch):
        cx, cy = self._p1_stick_center
        dx = touch.x - cx
        dy = touch.y - cy
        import math
        dist = math.sqrt(dx * dx + dy * dy)
        r = self._p1_stick_radius
        if dist > r:
            dx *= r / dist
            dy *= r / dist
            dist = r
        n = dist / r if r > 0 else 0
        if n < DEAD_ZONE:
            self._p1_stick_x = 0.0
            self._p1_stick_y = 0.0
        else:
            self._p1_stick_x = dx / r
            self._p1_stick_y = dy / r

    def _update_stick2(self, touch):
        cx, cy = self._p2_stick_center
        dx = touch.x - cx
        dy = touch.y - cy
        import math
        dist = math.sqrt(dx * dx + dy * dy)
        r = self._p2_stick_radius
        if dist > r:
            dx *= r / dist
            dy *= r / dist
            dist = r
        n = dist / r if r > 0 else 0
        if n < DEAD_ZONE:
            self._p2_stick_x = 0.0
            self._p2_stick_y = 0.0
        else:
            self._p2_stick_x = dx / r
            self._p2_stick_y = dy / r

    def _draw_controls(self):
        self.canvas.after.clear()
        with self.canvas.after:
            self._draw_stick(self._p1_stick_center, self._p1_stick_x, self._p1_stick_y, self._p1_stick_radius)
            self._draw_stick(self._p2_stick_center, self._p2_stick_x, self._p2_stick_y, self._p2_stick_radius)
            self._draw_buttons(self._p1_button_positions, self._p1_buttons)
            self._draw_buttons(self._p2_button_positions, self._p2_buttons)

    def _draw_stick(self, center, sx, sy, radius):
        cx, cy = center
        Color(0.15, 0.15, 0.15, 0.5)
        Line(circle=(cx, cy, radius), width=3)
        Color(0.5, 0.5, 0.5, 0.6)
        knob_x = cx + sx * radius
        knob_y = cy + sy * radius
        Ellipse(pos=(knob_x - 16, knob_y - 16), size=(32, 32))

    def _draw_buttons(self, positions, states):
        for name, (bx, by) in positions.items():
            pressed = states.get(name, False)
            r, g, b = {
                "jump": (0.3, 0.7, 0.3),
                "light": (0.3, 0.5, 1.0),
                "heavy": (0.8, 0.5, 0.2),
                "guard": (0.6, 0.6, 0.3),
                "dash": (0.5, 0.3, 0.8),
                "special": (0.9, 0.3, 0.3),
            }.get(name, (0.4, 0.4, 0.4))
            a = 0.9 if pressed else 0.4
            Color(r, g, b, a)
            Ellipse(pos=(bx - self._button_radius, by - self._button_radius),
                    size=(self._button_radius * 2, self._button_radius * 2))
            Color(1, 1, 1, 0.7 if pressed else 0.5)
            label_text = {
                "jump": "跳", "light": "轻", "heavy": "重",
                "guard": "防", "dash": "冲", "special": "必",
            }.get(name, "?")


class MechaFighterApp(App):
    def build(self):
        Window.size = (SCREEN_W, SCREEN_H)
        root = FloatLayout(size=(SCREEN_W, SCREEN_H))

        self.game = GameWidget()
        root.add_widget(self.game)

        self.controls = TouchControls()
        root.add_widget(self.controls)

        self._title_label = Label(
            text="MECHA FIGHTER",
            font_size=32,
            bold=True,
            size_hint=(None, None),
            size=(300, 50),
            pos=(SCREEN_W / 2 - 150, SCREEN_H - 60),
            color=(1, 1, 1, 1),
        )
        root.add_widget(self._title_label)

        self._sub_label = Label(
            text="TAP TO START",
            font_size=16,
            size_hint=(None, None),
            size=(200, 30),
            pos=(SCREEN_W / 2 - 100, SCREEN_H / 2 + 20),
            color=(0.8, 0.8, 0.8, 1),
        )
        root.add_widget(self._sub_label)

        self._countdown_label = Label(
            text="",
            font_size=48,
            bold=True,
            size_hint=(None, None),
            size=(200, 60),
            pos=(SCREEN_W / 2 - 100, SCREEN_H / 2),
            color=(1, 1, 0.5, 1),
        )
        root.add_widget(self._countdown_label)

        self._win_label = Label(
            text="",
            font_size=36,
            bold=True,
            size_hint=(None, None),
            size=(300, 50),
            pos=(SCREEN_W / 2 - 150, SCREEN_H / 2),
            color=(1, 0.8, 0.2, 1),
        )
        root.add_widget(self._win_label)

        Clock.schedule_interval(self._update_labels, 1.0 / 30.0)

        return root

    def on_touch_down(self, touch):
        if self.game._game_state == GameState.IDLE:
            self.game.start_game()
            return True
        return super().on_touch_down(touch)

    def _update_labels(self, dt):
        p1, p2 = self.controls.get_controls()
        self.game.set_controls(p1, p2)

        self.controls._draw_controls()

        if self.game._game_state == GameState.IDLE:
            self._title_label.text = "MECHA FIGHTER"
            self._title_label.opacity = 1
            self._sub_label.opacity = 1
            self._countdown_label.text = ""
            self._win_label.text = ""
        elif self.game._game_state == GameState.COUNTDOWN:
            self._title_label.opacity = 0
            self._sub_label.opacity = 0
            ct = self.game._countdown_timer
            if ct > 1:
                self._countdown_label.text = str(int(ct))
            elif ct > 0:
                self._countdown_label.text = "FIGHT!"
            else:
                self._countdown_label.text = ""
            self._win_label.text = ""
        elif self.game._game_state == GameState.FIGHTING:
            self._title_label.opacity = 0
            self._sub_label.opacity = 0
            self._countdown_label.text = ""
            self._win_label.text = ""
        elif self.game._game_state == GameState.WINNER:
            self._title_label.opacity = 0
            self._sub_label.opacity = 0
            self._countdown_label.text = ""
            self._win_label.text = f"P{self.game._winner_id} WIN!"


if __name__ == "__main__":
    MechaFighterApp().run()
```

- [ ] **Step 3: Verify the app at least imports and the window opens**

Run: `cd /workspace && timeout 3 python -c "
from kivy_app.main import MechaFighterApp
from kivy_app.game.engine import GameWidget, GameState
from kivy_app.game.controls import TouchControls
print('All imports OK')
" 2>&1 || true`

- [ ] **Step 4: Commit**

```bash
git add kivy_app/main.py
git commit -m "feat: add main entry point with dual touch controls and game overlay UI"
```

---

## Build & Run

After all tasks are complete:

```bash
cd /workspace
pip install kivy 2>/dev/null || true
python -m kivy_app.main
```

For headless CI verification (no display):
```bash
cd /workspace
python -c "
from kivy_app.game.fighter import Fighter, FighterState
from kivy_app.game.combat import CombatSystem, calculate_damage, Hitbox
print('All core modules load correctly')
f1 = Fighter(1, 100, 156)
f2 = Fighter(2, 200, 156)
f1.set_state(FighterState.LIGHT_ATTACK, 8)
cs = CombatSystem()
dmg = cs.check_hit(f1, f2)
print(f'Check hit damage: {dmg}')
print('All systems nominal')
"
```