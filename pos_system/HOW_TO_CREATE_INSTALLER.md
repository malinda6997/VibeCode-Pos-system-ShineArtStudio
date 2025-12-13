# How to Create Professional Windows Installer for Your Client

## Step 1: Download and Install Inno Setup (One-time setup)

1. Go to: **https://jrsoftware.org/isdl.php**
2. Download **Inno Setup 6** (free, about 3MB)
3. Install it on your computer

## Step 2: Create the Installer

1. Open **Inno Setup Compiler** (from Start Menu or Desktop)
2. Click **File** → **Open**
3. Browse to: `F:\2025 NEW PROJECTS\Pasindu\Shine Art Studio\pos_system\`
4. Select: **installer_script.iss**
5. Click **Build** → **Compile** (or press F9)
6. Wait 10-20 seconds while it builds

## Step 3: Get Your Installer

The installer will be created at:

```
F:\2025 NEW PROJECTS\Pasindu\Shine Art Studio\pos_system\installer_output\ShineArtStudio_POS_Setup.exe
```

## Step 4: Give to Your Client

Send your client the file: **ShineArtStudio_POS_Setup.exe**

### What Your Client Will Experience:

1. **Double-click** `ShineArtStudio_POS_Setup.exe`
2. **Installation Wizard** appears (professional Windows installer)
3. Choose installation location (default: `C:\Program Files\ShineArtStudio\`)
4. Choose shortcuts (Desktop + Start Menu)
5. Click **Install**
6. Installation completes with success message showing login credentials
7. Option to launch immediately

### After Installation:

- Desktop shortcut: "Shine Art Studio POS"
- Start Menu: All Programs → Shine Art Studio → Shine Art Studio POS
- Uninstall: Control Panel → Programs → Uninstall
- Database will be created on first run

## Default Login Info (shown after installation):

- **Admin:** username: `admin` | password: `admin123`
- **Staff:** username: `staff` | password: `staff123`

---

## Quick Command (Alternative)

If you have Inno Setup installed, you can also build from command line:

```powershell
cd "F:\2025 NEW PROJECTS\Pasindu\Shine Art Studio\pos_system"
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_script.iss
```

The installer is production-ready and looks professional like any commercial software!
