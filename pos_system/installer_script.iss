[Setup]
; Application Information
AppName=Shine Art Studio POS System
AppVersion=1.0.0
AppVerName=Shine Art Studio POS System 1.0.0
AppPublisher=Shine Art Studio
AppPublisherURL=https://github.com/malinda6997/Shine-art-Studio-post-system
AppSupportURL=https://github.com/malinda6997/Shine-art-Studio-post-system
AppUpdatesURL=https://github.com/malinda6997/Shine-art-Studio-post-system
AppCopyright=Copyright (C) 2025 Shine Art Studio

; Installation Directories
DefaultDirName={autopf}\ShineArtStudio
DefaultGroupName=Shine Art Studio
DisableProgramGroupPage=no
AllowNoIcons=yes
UsePreviousAppDir=yes

; Output Configuration
OutputDir=installer_output
OutputBaseFilename=ShineArtStudio_POS_Setup_v1.0.0
SetupIconFile=compiler:SetupClassicIcon.ico

; Compression
Compression=lzma2/max
SolidCompression=yes
LZMANumBlockThreads=2

; Visual Style
WizardStyle=modern
WizardImageFile=compiler:WizModernImage-IS.bmp
WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp
DisableWelcomePage=no
DisableReadyPage=no
DisableFinishedPage=no

; License
LicenseFile=LICENSE.txt

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Uninstall Configuration
UninstallDisplayIcon={app}\ShineArtStudio_POS.exe
UninstallDisplayName=Shine Art Studio POS System
UninstallFilesDir={app}\uninstall
CreateUninstallRegKey=yes

; Version Information
VersionInfoVersion=1.0.0.0
VersionInfoCompany=Shine Art Studio
VersionInfoDescription=Photography Studio Point of Sale System - Professional Edition
VersionInfoTextVersion=1.0.0
VersionInfoCopyright=Copyright (C) 2025 Shine Art Studio
VersionInfoProductName=Shine Art Studio POS System
VersionInfoProductVersion=1.0.0.0

; Disk Spanning
DiskSpanning=no
SlicesPerDisk=1

; Setup Appearance
ShowLanguageDialog=no
SetupLogging=yes
AppendDefaultDirName=no
DirExistsWarning=auto

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Types]
Name: "full"; Description: "Full Installation"
Name: "compact"; Description: "Compact Installation"
Name: "custom"; Description: "Custom Installation"; Flags: iscustom

; Main Application
Source: "dist\ShineArtStudio_POS.exe"; DestDir: "{app}"; Flags: ignoreversion; Components: main

; Documentation
Source: "README.md"; DestDir: "{app}\docs"; Flags: ignoreversion; Components: docs
Source: "LICENSE.txt"; DestDir: "{app}\docs"; Flags: ignoreversion; Components: docs
Source: "INSTALLATION_GUIDE.md"; DestDir: "{app}\docs"; Flags: ignoreversion isreadme; Components: docs

[Registry]
Root: HKLM; Subkey: "Software\ShineArtStudio"; Flags: uninsdeletekeyifempty
Root: HKLM; Subkey: "Software\ShineArtStudio\POS"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\ShineArtStudio\POS"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"
Root: HKLM; Subkey: "Software\ShineArtStudio\POS"; ValueType: string; ValueName: "Version"; ValueData: "1.0.0"

[Run]
Filename: "{app}\ShineArtStudio_POS.exe"; Description: "{cm:LaunchProgram,Shine Art Studio POS}"; Flags: nowait postinstall skipifsilent shellexec

[UninstallDelete]
Type: filesandordirs; Name: "{app}\database"
Type: filesandordirs; Name: "{app}\logs"

[Messages]
WelcomeLabel1=Welcome to Shine Art Studio POS System Setup
WelcomeLabel2=This will install [name/ver] on your computer.%n%nShine Art Studio POS is a professional point-of-sale system designed specifically for photography studios. It includes billing, invoicing, customer management, inventory tracking, and booking management.%n%nIt is recommended that you close all other applications before continuing.
FinishedHeadingLabel=Completing Shine Art Studio POS System Setup
FinishedLabelNoIcons=Setup has finished installing [name] on your computer. The application may be launched by selecting the installed shortcuts.
FinishedLabel=Setup has finished installing [name] on your computer. The application may be launched by selecting the installed icons.
ClickFinish=Click Finish to exit Setup.
SelectDirLabel3=Setup will install [name] into the following folder.
SelectDirBrowseLabel=To continue, click Next. If you would like to select a different folder, click Browse.

[Code]
var
  InfoPage: TOutputMsgMemoWizardPage;

procedure InitializeWizard;
begin
  // Create custom information page
  InfoPage := CreateOutputMsgMemoPage(wpWelcome,
    'Important Information', 
    'Please read the following important information before continuing.',
    'When you are ready to continue with Setup, click Next.' + #13#10#13#10 +
    'System Requirements:' + #13#10 +
    '• Windows 10 or Windows 11' + #13#10 +
    '• 4 GB RAM minimum' + #13#10 +
    '• 500 MB free disk space' + #13#10 +
    '• No internet connection required (fully offline)' + #13#10#13#10 +
    'Features:' + #13#10 +
    '• User Authentication (Admin & Staff roles)' + #13#10 +
    '• Customer Management' + #13#10 +
    '• Service & Frame Inventory Management' + #13#10 +
    '• Billing & PDF Invoice Generation' + #13#10 +
    '• Booking Management' + #13#10 +
    '• Invoice History & Reprinting' + #13#10 +
    '• Fully Offline Operation');
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  // Check Windows version
  if not IsWindows7OrLater() then
  begin
    MsgBox('This application requires Windows 7 or later.', mbError, MB_OK);
    Result := False;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Installation complete message
    MsgBox('Installation completed successfully!' + #13#10#13#10 + 
           'IMPORTANT - Default Login Credentials:' + #13#10#13#10 + 
           '▸ Admin Access:' + #13#10 + 
           '   Username: admin' + #13#10 + 
           '   Password: admin123' + #13#10#13#10 + 
           '▸ Staff Access:' + #13#10 + 
           '   Username: staff' + #13#10 + 
           '   Password: staff123' + #13#10#13#10 + 
           'Please change these passwords after first login for security.' + #13#10#13#10 +
           'The application has been installed to:' + #13#10 +
           ExpandConstant('{app}'), 
           mbInformation, MB_OK);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    if MsgBox('Do you want to delete the database and all user data?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      DelTree(ExpandConstant('{app}\database'), True, True, True);
      DelTree(ExpandConstant('{app}\invoices'), True, True, True);
      MsgBox('All user data has been removed.', mbInformation, MB_OK);
    end else
    begin
      MsgBox('User data has been preserved. You can find it at:' + #13#10 + ExpandConstant('{app}'), mbInformation, MB_OK);
    end;
  end;
end;

function GetUninstallString: string;
var
  sUnInstPath: string;
  sUnInstallString: String;
begin
  Result := '';
  sUnInstPath := ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{{#SetupSetting("AppId")}}_is1');
  sUnInstallString := '';
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;

function IsUpgrade: Boolean;
begin
  Result := (GetUninstallString() <> '');
end;

function InitializeUninstall(): Boolean;
begin
  Result := True;
  if MsgBox('Are you sure you want to completely remove Shine Art Studio POS and all of its components?', mbConfirmation, MB_YESNO) = IDNO then
    Result := False
; Quick Launch Icon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Shine Art Studio POS"; Filename: "{app}\ShineArtStudio_POS.exe"; WorkingDir: "{app}cked
Name: "startmenu"; Description: "Create Start Menu shortcuts"; GroupDescription: "Additional shortcuts:"; Flags: checkedonce

[Files]
Source: "dist\ShineArtStudio_POS.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Shine Art Studio POS"; Filename: "{app}\ShineArtStudio_POS.exe"
Name: "{group}\Uninstall Shine Art Studio POS"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Shine Art Studio POS"; Filename: "{app}\ShineArtStudio_POS.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Shine Art Studio POS"; Filename: "{app}\ShineArtStudio_POS.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\ShineArtStudio_POS.exe"; Description: "Launch Shine Art Studio POS System"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox('Installation completed successfully!' + #13#10 + #13#10 + 
           'Default Login Credentials:' + #13#10 + 
           'Admin - Username: admin, Password: admin123' + #13#10 + 
           'Staff - Username: staff, Password: staff123', 
           mbInformation, MB_OK);
  end;
end;
