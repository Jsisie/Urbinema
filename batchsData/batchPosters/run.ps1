param(
    [ValidateSet("generate", "fetch", "posters", "catalog", "all")]
    [string]$Action = "all",
    [int]$Limit = 0,
    [string]$Input = "",
    [switch]$Force,
    [switch]$DryRun,
    [switch]$NoPosters
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$python = $null
foreach ($candidate in @("python", "py")) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) {
        $python = $candidate
        break
    }
}
if (-not $python) {
    throw "Python 3 est requis. Installe-le puis relance ce script."
}

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Fichier .env cree. Ouvre-le, colle TMDB_API_KEY, puis relance."
    exit 1
}

$argsList = @("posters_batch.py", $Action)
if ($Input) { $argsList += @("--input", $Input) }
if ($Limit -gt 0) { $argsList += @("--limit", "$Limit") }
if ($Force) { $argsList += "--force" }
if ($DryRun) { $argsList += "--dry-run" }
if ($NoPosters) { $argsList += "--no-posters" }

if ($python -eq "py") {
    & py -3 @argsList
} else {
    & python @argsList
}
exit $LASTEXITCODE
