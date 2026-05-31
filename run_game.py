
#!/usr/bin/env python3
"""Pixel Mecha Fighter - Run Script"""
import sys
import os

# Configure Kivy for headless mode if needed (for servers)
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_NO_CONSOLELOG'] = '0'

# Add the kivy_app directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
kivy_app_dir = os.path.join(script_dir, 'kivy_app')
sys.path.insert(0, kivy_app_dir)

print("=" * 50)
print("  PIXEL MECHA FIGHTER")
print("=" * 50)
print()

try:
    from main import MechaFighterApp
    print("Starting game...")
    print()
    app = MechaFighterApp()
    app.run()
except KeyboardInterrupt:
    print("\nGame stopped by user.")
    sys.exit(0)
except Exception as e:
    print(f"\nError starting game: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
