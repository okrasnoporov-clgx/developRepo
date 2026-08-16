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


### Network testing
Test-NetConnection -ComputerName localhost -Port 27017

### Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))


choco install maven --install-directory="c:\tools\maven" -y