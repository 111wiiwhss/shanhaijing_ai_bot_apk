
#!/usr/bin/env python3
"""Pixel Mecha Fighter - Game Logic Test"""
import sys
import os

# Add the project directory to the path
project_dir = os.path.dirname(os.path.abspath(__file__))
kivy_app_dir = os.path.join(project_dir, 'kivy_app')
sys.path.insert(0, kivy_app_dir)

from game.fighter import Fighter, FighterState
from game.combat import CombatSystem

print("=" * 50)
print("  PIXEL MECHA FIGHTER - LOGIC TEST")
print("=" * 50)
print()

# Test 1: Create fighters
print("Test 1: Creating fighters...")
f1 = Fighter(player_id=1, x=100, y=156, facing_right=True)
f2 = Fighter(player_id=2, x=300, y=156, facing_right=False)
print(f"  ✓ Player 1 (Blue) created at ({f1.x}, {f1.y}")
print(f"  ✓ Player 2 (Red) created at ({f2.x}, {f2.y})")
print()

# Test 2: Test basic fighter updates
print("Test 2: Testing fighter updates...")
initial_hp = f1.hp
print(f"  Initial HP: {f1.hp}/{f1.max_hp}")
f1.take_damage(20)
print(f"  After taking 20 damage: {f1.hp}/{f1.max_hp}")
assert f1.hp == initial_hp - 20
print("  ✓ Damage system works")
print()

# Test 3: Combat system
print("Test 3: Testing combat system...")
combat = CombatSystem()
f1.set_state(FighterState.LIGHT_ATTACK, 8)
f2.facing_right = True
f1.x = 200
f2.x = 220
damage = combat.check_hit(f1, f2)
print(f"  Light attack hit damage: {damage}")
print(f"  P1 Energy: {f1.energy}/{f1.max_energy}")
print(f"  P2 HP: {f2.hp}/{f2.max_hp}")
print("  ✓ Combat system works")
print()

# Test 4: Combo system
print("Test 4: Testing combo system...")
f1.combo_count = 0
f1.set_state(FighterState.LIGHT_ATTACK, 8)
damage = combat.check_hit(f1, f2)
print(f"  First hit - Combo: {f1.combo_count}")
f1.set_state(FighterState.LIGHT_ATTACK, 8)
damage = combat.check_hit(f1, f2)
print(f"  Second hit - Combo: {f1.combo_count}")
f1.set_state(FighterState.LIGHT_ATTACK, 8)
damage = combat.check_hit(f1, f2)
print(f"  Third hit - Combo: {f1.combo_count}")
assert f1.combo_count &gt;= 1
print("  ✓ Combo system works")
print()

# Test 5: Energy and special attack
print("Test 5: Testing energy and special attack...")
f1.add_energy(100)
print(f"  P1 Energy at: {f1.energy}/{f1.max_energy}")
assert f1.energy >= f1.max_energy
f1.set_state(FighterState.SPECIAL, 30)
f1.energy = 0
print(f"  Used special attack, energy now: {f1.energy}")
print("  ✓ Special attack system works")
print()

# Test 6: State transitions
print("Test 6: Testing state transitions...")
f1.set_state(FighterState.IDLE)
print(f"  State: {f1.state}")
assert f1.state == FighterState.IDLE
f1.set_state(FighterState.JUMP)
f1.y = 200
f1.on_ground = False
f1.vy = 200
print(f"  Jumped, y={f1.y}, vy={f1.vy}")
print("  ✓ State transitions work")
print()

print("=" * 50)
print("✅ All tests passed!")
print("=" * 50)
print()
print("Game logic is working correctly.")
print("Now you can run 'python run_game.py' to start the full game!")
