
#!/usr/bin/env python3
import sys
import os

# Add the project directory to the path
project_dir = os.path.dirname(os.path.abspath(__file__))
kivy_app_dir = os.path.join(project_dir, 'kivy_app')
sys.path.insert(0, kivy_app_dir)

print('Testing imports from:', kivy_app_dir)
print('-' * 50)

try:
    from game.fighter import Fighter, FighterState
    print('✓ Fighter module imported successfully')
except Exception as e:
    print(f'✗ Failed to import Fighter: {e}')

try:
    from game.combat import CombatSystem
    print('✓ Combat module imported successfully')
except Exception as e:
    print(f'✗ Failed to import Combat: {e}')

try:
    from game.controls import ControlState
    print('✓ Controls module imported successfully')
except Exception as e:
    print(f'✗ Failed to import Controls: {e}')

try:
    from game.sprites import SpriteAnimator
    print('✓ Sprites module imported successfully')
except Exception as e:
    print(f'✗ Failed to import Sprites: {e}')

try:
    from game.scene import SceneRenderer
    print('✓ Scene module imported successfully')
except Exception as e:
    print(f'✗ Failed to import Scene: {e}')

try:
    from game.ui import draw_hud
    print('✓ UI module imported successfully')
except Exception as e:
    print(f'✗ Failed to import UI: {e}')

try:
    from game.engine import GameWidget, GameState
    print('✓ Engine module imported successfully')
except Exception as e:
    print(f'✗ Failed to import Engine: {e}')

print('\n' + '-' * 50)
print('Import testing complete!')
