"""
Build script to create executable for Shine Art Studio POS System
Run this file to generate the .exe file
"""
import PyInstaller.__main__
import os

# Get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# PyInstaller arguments
PyInstaller.__main__.run([
    'main.py',
    '--name=ShineArtStudio_POS',
    '--onefile',
    '--windowed',
    '--icon=NONE',
    f'--add-data=auth;auth',
    f'--add-data=database;database',
    f'--add-data=services;services',
    f'--add-data=ui;ui',
    '--hidden-import=customtkinter',
    '--hidden-import=reportlab',
    '--hidden-import=tkcalendar',
    '--hidden-import=babel.numbers',
    '--hidden-import=darkdetect',
    '--collect-all=customtkinter',
    '--collect-all=tkcalendar',
    '--noconfirm'
])

print("\n" + "="*60)
print("Build Complete!")
print("="*60)
print(f"\nExecutable file location:")
print(f"{os.path.join(current_dir, 'dist', 'ShineArtStudio_POS.exe')}")
print("\nYou can now run the .exe file directly!")
print("="*60)
