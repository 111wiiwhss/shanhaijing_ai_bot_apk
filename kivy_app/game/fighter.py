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