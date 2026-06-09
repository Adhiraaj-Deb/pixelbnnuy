"""
Pixelbnnuy – Desktop Pet Bunny
===============================
Entry point for the desktop pet application.
Generates assets on first run, then launches the bunny window.

Usage:
    python run.py
"""

import os
import sys

# Ensure project root is on the path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

if getattr(sys, 'frozen', False):
    # Running as PyInstaller executable
    # First check for an external assets folder for modding
    external_assets = os.path.join(os.path.dirname(sys.executable), "assets")
    if os.path.exists(external_assets) and os.path.isdir(external_assets):
        ASSETS_DIR = external_assets
    else:
        # Fall back to internal bundled assets
        ASSETS_DIR = os.path.join(sys._MEIPASS, "assets")
else:
    ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")


def ensure_assets():
    """Generate sprite assets if they don't exist."""
    if getattr(sys, 'frozen', False):
        return  # Assets are pre-packaged when frozen

    # Check for a key asset to determine if generation is needed
    check_file = os.path.join(ASSETS_DIR, "white_idle.png")
    if not os.path.exists(check_file):
        print("[Setup] First run detected - generating pixel art assets...")
        from generate_assets import generate_all_assets
        generate_all_assets()
    else:
        print("[Setup] Assets found.")


def main():
    """Launch the Pixelbnnuy desktop pet."""
    print("[Bunny] Starting Pixelbnnuy...")
    print("   Ctrl+C in terminal or close the window to exit.\n")

    # Generate assets if needed
    ensure_assets()

    # Import Qt after assets are ready
    from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
    from PySide6.QtGui import QIcon
    from PySide6.QtGui import QAction

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Pixelbnnuy")
    app.setQuitOnLastWindowClosed(True)

    # Setup System Tray
    tray_icon = QSystemTrayIcon(QIcon(os.path.join(ASSETS_DIR, 'icon.ico')), app)
    tray_icon.setToolTip("Pixelbnnuy")
    
    tray_menu = QMenu()
    
    def spawn_bunny():
        from app.window import BunnyWindow
        BunnyWindow(ASSETS_DIR)

    spawn_action = QAction("Spawn New Bunny")
    spawn_action.triggered.connect(spawn_bunny)
    tray_menu.addAction(spawn_action)
    
    quit_action = QAction("Close All Bunnies (Quit)")
    quit_action.triggered.connect(app.quit)
    tray_menu.addAction(quit_action)
    
    tray_icon.setContextMenu(tray_menu)
    tray_icon.show()

    # Launch first bunny window
    spawn_bunny()

    print("[Bunny] Bunny is alive! Interactions:")
    print("   - Hover over bunny -> petting reaction")
    print("   - Click bunny -> stretch animation")
    print("   - Click & drag -> move bunny (with squish!)")
    print("   - Triple-click -> change color palette")
    print("   - Type on keyboard -> typing reaction")
    print("   - Scroll mouse wheel -> ear bounce")
    print("   - Move cursor near bunny fast -> hunt mode")
    print()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
