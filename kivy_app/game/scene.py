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