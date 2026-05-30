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