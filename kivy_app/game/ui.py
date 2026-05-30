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