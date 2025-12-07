Set objShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Run the batch file silently
objShell.Run """" & scriptDir & "\Launch-TrayApp.bat""", 0, False

Set objShell = Nothing
Set fso = Nothing
