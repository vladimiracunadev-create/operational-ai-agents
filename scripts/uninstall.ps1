param([string]$Target = (Join-Path $env:USERPROFILE ".claude\agents"))
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Removed = 0
Get-ChildItem (Join-Path $RepoRoot "agents") -Directory | ForEach-Object {
    $Destination = Join-Path $Target ($_.Name + ".md")
    if (Test-Path $Destination) {
        $Item = Get-Item $Destination -Force
        $Managed = $Item.LinkType -eq "SymbolicLink" -or (Select-String -Path $Destination -Pattern "managed-by: operational-ai-agents" -Quiet)
        if ($Managed) {
            Remove-Item $Destination -Force
            $Removed++
        }
    }
}
Write-Host "Eliminados $Removed agentes administrados"
