[Setup]
AppId={{A13A6732-84A8-4DB9-B77B-ABICUT100001}
AppName=AbiCut
AppVersion=1.0.0
AppPublisher=Leon Stein

DefaultDirName={autopf}\AbiCut
DefaultGroupName=AbiCut

OutputDir=installer
OutputBaseFilename=AbiCut_Setup_1.0.0

SetupIconFile=assets\abicut_logo.ico
UninstallDisplayIcon={app}\AbiCut.exe

Compression=lzma2
SolidCompression=yes
WizardStyle=modern

PrivilegesRequired=admin

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

DisableProgramGroupPage=yes

VersionInfoVersion=1.0.0.0
VersionInfoProductName=AbiCut
VersionInfoProductVersion=1.0.0
VersionInfoDescription=AbiCut - Music & Presentation Controller
VersionInfoCompany=Leon Stein

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "Desktop-Verknüpfung erstellen"; GroupDescription: "Zusätzliche Verknüpfungen:"; Flags: unchecked

[Files]
Source: "dist\AbiCut\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\AbiCut"; Filename: "{app}\AbiCut.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\AbiCut"; Filename: "{app}\AbiCut.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\AbiCut.exe"; Description: "AbiCut starten"; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent