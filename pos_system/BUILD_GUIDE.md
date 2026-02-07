# 🎯 Shine Art Studio POS - Standalone EXE Build Guide

## 📋 Overview
This guide explains how to build a **single-file, portable, standalone EXE** for the Shine Art Studio POS System. The resulting EXE is **100% self-contained** and can run on any Windows PC without installation.

---

## ✨ Features of the Standalone EXE

### ✅ Plug & Play
- **Single File**: One EXE file - no dependencies needed
- **No Installation**: Just double-click to run
- **Fully Portable**: Copy to USB, network drive, or any folder
- **Auto-Database**: Creates `pos_database.db` automatically on first run

### 🔒 Embedded Assets
All images and resources are **embedded inside the EXE**:
- ✓ Login screen background
- ✓ Studio logos
- ✓ Application icons
- ✓ Bill/Invoice logos

### 🎨 User Experience
- **No Console Window**: Clean GUI-only application
- **Auto-Focus**: Login field is automatically selected
- **Professional**: Windows taskbar icon and proper branding

---

## 🛠️ Building the EXE

### **Method 1: Using the Batch File (Easiest)**
1. Double-click `BUILD_EXE.bat`
2. Wait for the build to complete
3. Find your EXE in the `dist/` folder

### **Method 2: Using Python Script**
```bash
python build_standalone_exe.py
```

### **Method 3: Manual PyInstaller Command**
```bash
pyinstaller --noconfirm --onefile --windowed --add-data "assets;assets" --icon="assets/logos/app_icon.ico" --name "ShineArt_POS" main.py
```

---

## 📦 Requirements

### Python Packages
```bash
pip install customtkinter Pillow reportlab pyinstaller
```

### Asset Files
The following files must exist in `assets/` folder:
- `assets/logos/app_icon.ico` - Main application icon
- `assets/logos/appLogo.ico` - Alternate icon
- `assets/logos/studio-logo.png` - Studio branding logo
- `assets/logos/billLogo.png` - Bill template logo
- `assets/logos/invoiceLogo.png` - Invoice template logo
- `assets/login_images/loginimage01.jpg` - Login background

---

## 🚀 What Happens During Build?

1. **Cleanup**: Removes old `build/` and `dist/` folders
2. **Verification**: Checks all packages and assets
3. **Bundling**: PyInstaller packages everything into one EXE
4. **Embedding**: All assets are embedded using `resource_path()` utility
5. **Output**: Creates `dist/ShineArt_POS.exe` (~80-120 MB)

---

## 📁 Output Structure

```
dist/
└── ShineArt_POS.exe    ← This is your standalone application!
```

---

## 🎯 Deployment Instructions

### For the User:
1. Copy `ShineArt_POS.exe` to any folder on their PC
2. Double-click `ShineArt_POS.exe` to run
3. Login with credentials:
   - **Default Username**: `admin`
   - **Default Password**: `yourpassword` (check your database setup)
4. Database file `pos_database.db` will be created automatically

### For You (Developer):
- Test the EXE on a **clean Windows PC** without Python installed
- Verify all images load correctly
- Test database creation on first run
- Check that the app icon appears in taskbar

---

## 🔧 Technical Details

### Resource Path Resolution
All asset paths use the `resource_path()` function from `utils/resource_path.py`:

```python
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except AttributeError:
        base_path = os.path.abspath(".")  # Development mode
    return os.path.join(base_path, relative_path)
```

This ensures assets work in both:
- **Development Mode**: Reading from `assets/` folder
- **EXE Mode**: Reading from PyInstaller's temporary extraction folder

### Database Auto-Creation
The application automatically creates the database if missing:
```python
def main():
    from database import initialize_database
    initialize_database()  # Creates pos_database.db if not exists
    app = MainApplication()
    app.mainloop()
```

### Focus Enhancement
Login window automatically focuses on username field:
```python
self.after(100, lambda: self.username_entry.focus())
```

---

## 🏢 Business Details (Hardcoded)

All PDFs, reports, and invoices include:
- **Studio Name**: STUDIO SHINE ART
- **Address**: No: 52/1/1, Maravila Road, Nattandiya
- **Contact**: 0767898604 / 0322051680
- **Developer**: Malinda Prabath

---

## ❓ Troubleshooting

### "Missing DLL" Error
- Install **Microsoft Visual C++ Redistributable**
- Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe

### Images Not Showing
- Verify `assets/` folder structure
- Check that `resource_path()` is used for all image paths
- Rebuild with `--add-data "assets;assets"`

### EXE Won't Start
- Run from Command Prompt to see error messages
- Check Windows Defender/Antivirus isn't blocking it
- Try running as Administrator

### Database Not Created
- Check folder permissions (needs write access)
- Look for `pos_database.db` in same folder as EXE
- Check console output (if running from terminal)

---

## 📊 Expected File Sizes

- **EXE Size**: ~80-120 MB (includes Python runtime + all packages + assets)
- **Database Size**: Starts at ~100 KB, grows with usage
- **Memory Usage**: ~150-300 MB while running

---

## 🎉 Success Checklist

After building, verify:
- [ ] EXE file exists in `dist/` folder
- [ ] Icon appears correctly in taskbar
- [ ] Login screen shows background image
- [ ] Studio logo displays in sidebar
- [ ] Bills and invoices generate with logos
- [ ] Database auto-creates on first run
- [ ] Application runs on a PC **without Python**

---

## 📞 Support

**Developer**: Malinda Prabath  
**Application**: Shine Art Studio POS System  
**Year**: 2025

For technical support, refer to the main application documentation or contact the developer.

---

## 🔄 Version Notes

- **Build Type**: Single-file standalone EXE (`--onefile`)
- **GUI Mode**: Windowed (no console)
- **Asset Bundling**: Fully embedded
- **Portability**: 100% portable
- **Installation**: Not required

---

Made with ❤️ for **Shine Art Studio**  
© 2025 Photography Studio Management System
