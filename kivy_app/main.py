from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label, CoreLabel
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.core.window import Window
from kivy.clock import Clock
import math

from game.engine import GameWidget, GameState, GAME_W, GAME_H, SCREEN_W, SCREEN_H
from game.controls import ControlState, DEAD_ZONE


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

        self._p1_stick_center = (120, 120)
        self._p1_stick_radius = 80
        self._p2_stick_center = (SCREEN_W - 120, 120)
        self._p2_stick_radius = 80
        self._button_radius = 32

        self._layout_buttons()

    def _layout_buttons(self):
        cx1, cy1 = self._p1_stick_center

        self._p1_button_positions = {
            "jump": (cx1 + 180, cy1 + 100),
            "light": (cx1 + 260, cy1 + 100),
            "guard": (cx1 + 180, cy1 + 10),
            "heavy": (cx1 + 260, cy1 + 10),
            "dash": (cx1 + 180, cy1 - 80),
            "special": (cx1 + 260, cy1 - 80),
        }

        cx2, cy2 = self._p2_stick_center
        self._p2_button_positions = {
            "jump": (cx2 - 260, cy2 + 100),
            "light": (cx2 - 180, cy2 + 100),
            "guard": (cx2 - 260, cy2 + 10),
            "heavy": (cx2 - 180, cy2 + 10),
            "dash": (cx2 - 260, cy2 - 80),
            "special": (cx2 - 180, cy2 - 80),
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
        return (x - cx) ** 2 + (y - cy) ** 2 <= (self._p1_stick_radius * 1.3) ** 2

    def _is_in_stick2(self, x, y):
        cx, cy = self._p2_stick_center
        return (x - cx) ** 2 + (y - cy) ** 2 <= (self._p2_stick_radius * 1.3) ** 2

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

        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.uid == self._p1_stick_touch:
            self._update_stick1(touch)
            return True
        if touch.uid == self._p2_stick_touch:
            self._update_stick2(touch)
            return True
        return super().on_touch_move(touch)

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

        return super().on_touch_up(touch)

    def _update_stick1(self, touch):
        cx, cy = self._p1_stick_center
        dx = touch.x - cx
        dy = touch.y - cy
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
        r = self._button_radius
        with self.canvas.after:
            self._draw_stick(self._p1_stick_center, self._p1_stick_x, self._p1_stick_y, self._p1_stick_radius)
            self._draw_stick(self._p2_stick_center, self._p2_stick_x, self._p2_stick_y, self._p2_stick_radius)

            for name, (bx, by) in self._p1_button_positions.items():
                pressed = self._p1_buttons[name]
                rcol, gcol, bcol = {
                    "jump": (0.3, 0.8, 0.3),
                    "light": (0.3, 0.5, 1.0),
                    "heavy": (0.9, 0.5, 0.2),
                    "guard": (0.7, 0.7, 0.3),
                    "dash": (0.5, 0.3, 0.9),
                    "special": (1.0, 0.4, 0.2),
                }[name]
                alpha = 1.0 if pressed else 0.4
                Color(rcol, gcol, bcol, alpha)
                Ellipse(pos=(bx - r, by - r), size=(r * 2, r * 2))

            for name, (bx, by) in self._p2_button_positions.items():
                pressed = self._p2_buttons[name]
                rcol, gcol, bcol = {
                    "jump": (0.3, 0.8, 0.3),
                    "light": (0.3, 0.5, 1.0),
                    "heavy": (0.9, 0.5, 0.2),
                    "guard": (0.7, 0.7, 0.3),
                    "dash": (0.5, 0.3, 0.9),
                    "special": (1.0, 0.4, 0.2),
                }[name]
                alpha = 1.0 if pressed else 0.4
                Color(rcol, gcol, bcol, alpha)
                Ellipse(pos=(bx - r, by - r), size=(r * 2, r * 2))

    def _draw_stick(self, center, sx, sy, radius):
        cx, cy = center
        Color(0.1, 0.1, 0.1, 0.5)
        Line(circle=(cx, cy, radius), width=3)
        Color(0.4, 0.4, 0.4, 0.45)
        Ellipse(pos=(cx - radius, cy - radius), size=(radius * 2, radius * 2))
        Color(0.7, 0.7, 0.7, 0.7)
        knob_x = cx + sx * radius
        knob_y = cy + sy * radius
        Ellipse(pos=(knob_x - 18, knob_y - 18), size=(36, 36))


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
            font_size=36,
            bold=True,
            size_hint=(None, None),
            size=(400, 60),
            pos=(SCREEN_W / 2 - 200, SCREEN_H * 0.68),
            color=(1, 1, 1, 1),
        )
        root.add_widget(self._title_label)

        self._sub_label = Label(
            text="TAP TO START",
            font_size=18,
            size_hint=(None, None),
            size=(200, 30),
            pos=(SCREEN_W / 2 - 100, SCREEN_H * 0.52),
            color=(0.8, 0.8, 0.8, 1),
        )
        root.add_widget(self._sub_label)

        self._countdown_label = Label(
            text="",
            font_size=60,
            bold=True,
            size_hint=(None, None),
            size=(300, 80),
            pos=(SCREEN_W / 2 - 150, SCREEN_H * 0.50),
            color=(1, 1, 0.5, 1),
        )
        root.add_widget(self._countdown_label)

        self._win_label = Label(
            text="",
            font_size=40,
            bold=True,
            size_hint=(None, None),
            size=(400, 60),
            pos=(SCREEN_W / 2 - 200, SCREEN_H * 0.52),
            color=(1, 0.8, 0.2, 1),
        )
        root.add_widget(self._win_label)

        self._p1_label = Label(
            text="P1",
            font_size=14,
            size_hint=(None, None),
            size=(40, 20),
            pos=(self.controls._p1_button_positions["jump"][0] + 30, self.controls._p1_button_positions["jump"][1] + 40),
            color=(0.3, 0.5, 1.0, 1),
        )
        root.add_widget(self._p1_label)

        self._p2_label = Label(
            text="P2",
            font_size=14,
            size_hint=(None, None),
            size=(40, 20),
            pos=(self.controls._p2_button_positions["jump"][0] - 70, self.controls._p2_button_positions["jump"][1] + 40),
            color=(1.0, 0.4, 0.2, 1),
        )
        root.add_widget(self._p2_label)

        button_texts = {
            "jump": "JMP",
            "light": "L-ATK",
            "heavy": "H-ATK",
            "guard": "GRD",
            "dash": "DSH",
            "special": "SPC",
        }
        for name, (bx, by) in self.controls._p1_button_positions.items():
            lbl = Label(text=button_texts[name], font_size=9, size_hint=(None, None),
                       size=(60, 15), pos=(bx - 30, by - 22), color=(1, 1, 1, 0.6))
            root.add_widget(lbl)
        for name, (bx, by) in self.controls._p2_button_positions.items():
            lbl = Label(text=button_texts[name], font_size=9, size_hint=(None, None),
                       size=(60, 15), pos=(bx - 30, by - 22), color=(1, 1, 1, 0.6))
            root.add_widget(lbl)

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

        gs = self.game._game_state
        if gs == GameState.IDLE:
            self._title_label.opacity = 1
            self._sub_label.opacity = 1
            self._countdown_label.text = ""
            self._win_label.text = ""
        elif gs == GameState.COUNTDOWN:
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
        elif gs == GameState.FIGHTING:
            self._title_label.opacity = 0
            self._sub_label.opacity = 0
            self._countdown_label.text = ""
            self._win_label.text = ""
        elif gs == GameState.WINNER:
            self._title_label.opacity = 0
            self._sub_label.opacity = 0
            self._countdown_label.text = ""
            self._win_label.text = f"P{self.game._winner_id} WIN!"


if __name__ == "__main__":
    MechaFighterApp().run()