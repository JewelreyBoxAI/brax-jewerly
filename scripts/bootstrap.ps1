$ErrorActionPreference = "Stop"
function Log($l,$m){$t=(Get-Date).ToString("yyyy-MM-dd HH:mm:ss");Write-Host "[$t][$l] $m"}
try{
  if(-not(Test-Path .\.venv)){ Log INFO "Creating venv"; py -3.11 -m venv .venv }
  .\.venv\Scripts\Activate.ps1
  Log INFO "Upgrading pip"; python -m pip install --upgrade pip
  Log INFO "Installing deps"; pip install -r requirements.txt
  if(-not(Test-Path .env)){ Copy-Item .env.example .env }
  Log INFO "Bootstrap complete"
}catch{ Write-Host "[$(Get-Date -f 'yyyy-MM-dd HH:mm:ss')][ERROR] ☠️ $($_.Exception.Message)"; exit 1 }