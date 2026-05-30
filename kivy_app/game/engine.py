from enum import Enum, auto
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, PushMatrix, PopMatrix, Translate, Scale
from kivy.core.window import Window

from .fighter import (
    Fighter,
    FighterState,
    GROUND_Y,
    MOVE_SPEED,
    JUMP_VELOCITY,
    DASH_SPEED,
    DASH_DURATION,
    STAMINA_DASH_COST,
)
from .combat import CombatSystem, LIGHT_DURATION, HEAVY_DURATION, SPECIAL_DURATION
from .controls import ControlState
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
        Window.size = (SCREEN_W, SCREEN_H)

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

        Clock.schedule_interval(self._update, 1.0 / 60.0)

    def set_controls(self, p1: ControlState, p2: ControlState):
        self._p1_controls = p1
        self._p2_controls = p2

    def _update(self, dt):
        f1, f2 = self.fighters

        if self._game_state == GameState.IDLE:
            f1.update(dt)
            f2.update(dt)
        elif self._game_state == GameState.COUNTDOWN:
            self._countdown_timer -= dt
            if self._countdown_timer <= 0:
                self._game_state = GameState.FIGHTING
            f1.update(dt)
            f2.update(dt)
        elif self._game_state == GameState.FIGHTING:
            self._process_input(f1, self._p1_controls, f2)
            self._process_input(f2, self._p2_controls, f1)

            f1.facing_right = f2.x > f1.x
            f2.facing_right = f1.x > f2.x

            f1.update(dt)
            f2.update(dt)

            dmg1 = self.combat.check_hit(f1, f2)
            dmg2 = self.combat.check_hit(f2, f1)

            if dmg1:
                self.scene.spawn_hit_particles(f2.x, f2.y)
            if dmg2:
                self.scene.spawn_hit_particles(f1.x, f1.y)

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
        if f.state == FighterState.HURT:
            if f.state_timer <= 0:
                f.set_state(FighterState.IDLE)
            return

        if f.state == FighterState.SPECIAL:
            if f.state_timer <= 0:
                f.set_state(FighterState.IDLE)
            return

        attacking = f.state in (FighterState.LIGHT_ATTACK, FighterState.HEAVY_ATTACK)
        if attacking and f.state_timer > 0:
            return

        if f.state == FighterState.DASH and f.state_timer > 0:
            return

        if f.state == FighterState.GUARD:
            if not ctrl.guard:
                f.set_state(FighterState.IDLE)
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

        if ctrl.jump and f.on_ground:
            f.vy = JUMP_VELOCITY
            f.on_ground = False
            f.set_state(FighterState.JUMP)
        elif ctrl.jump and f.jump_count < 1 and f.vy < 100:
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
            FighterState.GUARD,
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