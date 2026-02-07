"""
Build Script for Shine Art Studio POS System
Creates a standalone, portable, single-file EXE that's "Plug & Play"

Developer: Malinda Prabath
Date: 2025

This script:
1. Cleans previous builds
2. Generates a standalone EXE with all assets embedded
3. Uses PyInstaller with --onefile and --windowed flags
4. Ensures all images and resources are bundled correctly
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def clean_build_folders():
    """Remove previous build artifacts"""
    print("🧹 Cleaning previous build artifacts...")
    folders_to_clean = ['build', 'dist']
    files_to_clean = ['ShineArt_POS.spec']
    
    for folder in folders_to_clean:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   ✓ Removed {folder}/")
    
    for file in files_to_clean:
        if os.path.exists(file):
            os.remove(file)
            print(f"   ✓ Removed {file}")
    
    print("✅ Build cleanup complete!\n")


def verify_requirements():
    """Verify all required packages are installed"""
    print("🔍 Verifying required packages...")
    
    # Map package names to their actual import names
    required_packages = {
        'customtkinter': 'customtkinter',
        'Pillow': 'PIL',  # Pillow imports as PIL
        'reportlab': 'reportlab',
        'pyinstaller': 'PyInstaller'  # pyinstaller imports as PyInstaller
    }
    
    missing_packages = []
    
    for package, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"   ✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ✗ {package} - MISSING")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All required packages are installed!\n")
    return True


def verify_assets():
    """Verify all required asset files exist"""
    print("🖼️  Verifying asset files...")
    
    required_assets = [
        'assets/logos/app_icon.ico',
        'assets/logos/appLogo.ico',
        'assets/logos/studio-logo.png',
        'assets/logos/billLogo.png',
        'assets/logos/invoiceLogo.png',
        'assets/login_images/loginimage01.jpg'
    ]
    
    missing_assets = []
    
    for asset in required_assets:
        if os.path.exists(asset):
            print(f"   ✓ {asset}")
        else:
            missing_assets.append(asset)
            print(f"   ⚠️  {asset} - MISSING (will use fallback)")
    
    if missing_assets:
        print(f"\n⚠️  Some assets are missing but build will continue with fallbacks")
    else:
        print("✅ All assets verified!\n")
    
    return True


def build_exe():
    """Build the standalone EXE using PyInstaller"""
    print("🔨 Building standalone EXE...\n")
    print("=" * 60)
    print("   SHINE ART STUDIO - POS SYSTEM")
    print("   Single-File Executable Build")
    print("   Developer: Malinda Prabath")
    print("=" * 60)
    print()
    
    # PyInstaller command with all necessary options
    cmd = [
        'pyinstaller',
        '--noconfirm',              # Don't ask for confirmation
        '--onefile',                # Create a single EXE file
        '--windowed',               # No console window (GUI only)
        '--add-data', 'assets;assets',  # Include assets folder
        '--icon=assets/logos/app_icon.ico',  # Application icon
        '--name', 'ShineArt_POS',   # Output EXE name
        'main.py'                   # Entry point
    ]
    
    print("📦 PyInstaller Command:")
    print("   " + " ".join(cmd))
    print()
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)
        
        print("\n" + "=" * 60)
        print("✅ BUILD SUCCESSFUL!")
        print("=" * 60)
        print()
        print("📁 Output Location:")
        print(f"   {os.path.abspath('dist/ShineArt_POS.exe')}")
        print()
        print("📊 File Size:")
        exe_path = 'dist/ShineArt_POS.exe'
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"   {size_mb:.2f} MB")
        print()
        print("🎯 Next Steps:")
        print("   1. Copy 'ShineArt_POS.exe' from the 'dist' folder")
        print("   2. Paste it anywhere on any Windows PC")
        print("   3. Double-click to run - No installation needed!")
        print("   4. Database will be auto-created in the same folder")
        print()
        print("✨ The application is now 100% portable!")
        print()
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print("❌ BUILD FAILED!")
        print("=" * 60)
        print(f"\nError: {e}")
        return False
    except FileNotFoundError:
        print("\n" + "=" * 60)
        print("❌ PYINSTALLER NOT FOUND!")
        print("=" * 60)
        print("\nPlease install PyInstaller:")
        print("   pip install pyinstaller")
        return False


def main():
    """Main build process"""
    print()
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  SHINE ART STUDIO - POS SYSTEM BUILD SCRIPT".center(58) + "║")
    print("║" + "  Standalone EXE Builder".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # Step 1: Clean previous builds
    clean_build_folders()
    
    # Step 2: Verify requirements
    if not verify_requirements():
        sys.exit(1)
    
    # Step 3: Verify assets
    verify_assets()
    
    # Step 4: Build EXE
    if build_exe():
        print("🎉 Build process completed successfully!")
        print()
        input("Press Enter to exit...")
        sys.exit(0)
    else:
        print("❌ Build process failed!")
        print()
        input("Press Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()
