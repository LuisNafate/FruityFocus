"""
Build script to package FruityFocus into a standalone Windows .exe using PyInstaller.
"""
import subprocess
import sys
import os

def build_exe():
    print("Building FruityFocus standalone executable...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, "assets", "icon.ico")
    assets_src = os.path.join(base_dir, "assets")

    # Add-data parameter for Windows uses semicolon ';'
    data_arg = f"{assets_src};assets"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",            # Standalone single .exe
        "--windowed",           # no console window
        f"--icon={icon_path}",
        f"--add-data={data_arg}",
        "--name=FruityFocus",
        os.path.join(base_dir, "main.py")
    ]

    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=base_dir)
    if result.returncode == 0:
        print("\nBuild completed successfully!")
        print(f"Executable output is located in: {os.path.join(base_dir, 'dist', 'FruityFocus')}")
    else:
        print(f"\nBuild failed with exit code: {result.returncode}")

if __name__ == "__main__":
    build_exe()
