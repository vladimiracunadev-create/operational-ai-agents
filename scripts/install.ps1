param([string]$Target = (Join-Path $env:USERPROFILE ".claude\agents"))
$RepoRoot = Split-Path -Parent $PSScriptRoot
New-Item -ItemType Directory -Force -Path $Target | Out-Null
$Conflicts = 0
Get-ChildItem (Join-Path $RepoRoot "agents") -Directory | ForEach-Object {
    $Source = Join-Path $_.FullName "AGENT.md"
    $Destination = Join-Path $Target ($_.Name + ".md")
    if (Test-Path $Destination) {
        $Item = Get-Item $Destination -Force
        $Managed = $Item.LinkType -eq "SymbolicLink" -or (Select-String -Path $Destination -Pattern "managed-by: operational-ai-agents" -Quiet)
        if (-not $Managed) {
            Write-Error "CONFLICTO: se preservó $Destination"
            $Conflicts++
            return
        }
        Remove-Item $Destination -Force
    }
    try {
        New-Item -ItemType SymbolicLink -Path $Destination -Target $Source -ErrorAction Stop | Out-Null
    } catch {
        Copy-Item $Source $Destination -Force
    }
}
if ($Conflicts -gt 0) { exit 2 }
Write-Host "Instalados en: $Target"
