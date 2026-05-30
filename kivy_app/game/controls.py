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
        self.bind(pos=self._on_change, size=self._on_change,
                  stick_x=self._on_change, stick_y=self._on_change)

    def _on_change(self, *args):
        self._center_x = self.x + self.width / 2
        self._center_y = self.y + self.height / 2
        self.radius = min(self.width, self.height) / 2 - 4
        self._draw()

    def _draw(self):
        self.canvas.clear()
        with self.canvas:
            Color(0.3, 0.3, 0.3, 0.5)
            Line(circle=(self._center_x, self._center_y, self.radius), width=3)
            Color(0.6, 0.6, 0.6, 0.7)
            sx = self._center_x + self.stick_x * self.radius
            sy = self._center_y + self.stick_y * self.radius
            Ellipse(pos=(sx - 14, sy - 14), size=(28, 28))

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

    def __init__(self, label="", **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.bind(pressed=self._on_change, pos=self._on_change,
                  size=self._on_change)

    def _on_change(self, *args):
        self._draw()

    def _draw(self):
        self.canvas.clear()
        with self.canvas:
            c = (0.2, 0.7, 0.2, 0.6) if self.pressed else (0.3, 0.3, 0.3, 0.5)
            Color(*c)
            from kivy.graphics import Rectangle
            Rectangle(pos=self.pos, size=self.size)

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