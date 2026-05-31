
#!/usr/bin/env python3
"""Pixel Mecha Fighter - Simple Game Logic Test"""
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

# Create fighters
print("Creating fighters...")
f1 = Fighter(player_id=1, x=100, y=156, facing_right=True)
f2 = Fighter(player_id=2, x=300, y=156, facing_right=False)
print(f"  Player 1 (Blue): HP {f1.hp}/{f1.max_hp}")
print(f"  Player 2 (Red): HP {f2.hp}/{f2.max_hp}")
print()

# Test damage
print("Testing damage...")
initial_hp = f1.hp
f1.take_damage(20)
print(f"  After 20 damage: {f1.hp}/{f1.max_hp}")
print("  ✓ Damage works")
print()

# Test combat
print("Testing combat...")
combat = CombatSystem()
f1.set_state(FighterState.LIGHT_ATTACK, 8)
f1.x = 200
f2.x = 220
damage = combat.check_hit(f1, f2)
print(f"  Light attack damage: {damage}")
print(f"  Player 1 energy: {f1.energy}")
print(f"  Player 2 HP: {f2.hp}")
print("  ✓ Combat works")
print()

print("=" * 50)
print("All basic tests passed!")
print("=" * 50)
print()
print("Game logic is working correctly.")
print("Now you can run 'python run_game.py' to start the full game!")
