# DownloadsOrganizeR .NET Service Host

## Overview
A Windows-native .NET 8 Worker Service that supervises the Python `Organizer.py` process, providing clean service installation without NSSM.

- Uses Windows Service hosting (`Microsoft.Extensions.Hosting.WindowsServices`)
- Writes stdout/stderr to `C:\Scripts\service-logs` (same convention)
- Self-contained single-file publish for easy deployment

## Structure
- `DownloadsOrganizeR.ServiceHost/` — .NET Worker Service
  - `Program.cs` — service entrypoint and Python process supervisor
  - `appsettings.json` — paths and behavior configuration
  - `Install-Service.ps1` — publish and install as Windows service

## Build & Install (Windows)

Prereqs:
- .NET SDK 8.x
- Python and the app deployed to `C:\Scripts`

Steps:
```powershell
cd dotnet/DownloadsOrganizeR.ServiceHost
# Publish self-contained single-file exe
PowerShell -ExecutionPolicy Bypass -File .\Install-Service.ps1 `
  -ServiceName DownloadsOrganizer `
  -PythonExe 'C:\Scripts\venv\Scripts\python.exe' `
  -ScriptPath 'C:\Scripts\Organizer.py' `
  -WorkingDirectory 'C:\Scripts'
```

## Update Configuration
Modify `appsettings.json` in the publish output folder to change paths or restart behavior, then restart the service:
```powershell
sc.exe stop DownloadsOrganizer
sc.exe start DownloadsOrganizer
```

## Uninstall Service
```powershell
sc.exe stop DownloadsOrganizer
sc.exe delete DownloadsOrganizer
```

## Next Steps
- Optionally port the organizer logic to .NET for native file watching
- Later migrate the Flask dashboard to ASP.NET Core
