### PS CLI Alias
Temporary: 
  Set-Alias k kubectl
Persistent:
  Test-Path $PROFILE
  New-Item -Path $PROFILE -ItemType File -Force
  code $PROFILE
  Set-Alias k kubectl
[Enable Scripts]:
    Get-ExecutionPolicy -List
    Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned


### kubectl Editor setup
[Environment]::SetEnvironmentVariable("KUBE_EDITOR", "vim", "User")

