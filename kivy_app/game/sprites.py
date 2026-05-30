from kivy.graphics import Color, Rectangle, PushMatrix, PopMatrix, Rotate, Translate
from kivy.graphics.instructions import InstructionGroup

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
        cx += 12 * scale

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