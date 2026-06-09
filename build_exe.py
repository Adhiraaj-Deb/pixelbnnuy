import os
import subprocess
import sys

def main():
    print("Building Pixelbnnuy Executable...")

    # Ensure pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Ensure assets are generated
    import generate_assets
    generate_assets.generate_all_assets()

    # PyInstaller command
    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",         # No terminal window
        "--onefile",           # Bundle everything into a single .exe
        "--icon=assets/icon.ico",
        "--add-data=assets;assets", # Bundle assets directory
        "--name=Pixelbnnuy",
        "--clean",
        "run.py"
    ]

    print(f"Running: {' '.join(args)}")
    subprocess.check_call(args)

    print("\nBuild complete! The executable is located in the 'dist' folder.")

if __name__ == "__main__":
    main()
