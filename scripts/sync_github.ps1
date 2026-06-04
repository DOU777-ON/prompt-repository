param(
    [string]$RemoteUrl,
    [string]$Branch = "main",
    [string]$CommitMessage,
    [string]$RepoRoot
)

$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
    $RepoRoot = Split-Path -Parent $PSScriptRoot
}

function Resolve-GitCommand {
    $git = Get-Command git -ErrorAction SilentlyContinue
    if ($git) {
        return $git.Source
    }

    $candidates = @(
        "C:\Program Files\Git\cmd\git.exe",
        "C:\Program Files\Git\bin\git.exe",
        "C:\Program Files (x86)\Git\cmd\git.exe",
        "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe"
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -Path $candidate) {
            return $candidate
        }
    }

    $githubDesktopGit = Get-ChildItem -Path "$env:LOCALAPPDATA\GitHubDesktop\app-*\resources\app\git\cmd\git.exe" -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending |
        Select-Object -First 1
    if ($githubDesktopGit) {
        return $githubDesktopGit.FullName
    }

    throw "git is not available on PATH and no GitHub Desktop bundled git was found."
}

$git = Resolve-GitCommand
Write-Host "Using git: $git"

Push-Location $RepoRoot
try {
    if (-not (Test-Path -Path ".git")) {
        & $git init | Out-Host
    }

    $currentBranch = & $git branch --show-current
    if (-not $currentBranch) {
        & $git checkout -B $Branch | Out-Host
    } elseif ($currentBranch -ne $Branch) {
        & $git branch -M $Branch | Out-Host
    }

    if ($RemoteUrl) {
        $existingRemote = & $git remote
        if ($existingRemote -contains "origin") {
            & $git remote set-url origin $RemoteUrl
        } else {
            & $git remote add origin $RemoteUrl
        }
    }

    & $git status --short | Out-Host
    & $git add -A

    & $git diff --cached --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "No changes to sync."
    } else {
        if (-not $CommitMessage) {
            $CommitMessage = "Update prompt repository $(Get-Date -Format yyyy-MM-dd)"
        }
        & $git commit -m $CommitMessage | Out-Host
    }

    $remotes = & $git remote
    if ($remotes -contains "origin") {
        & $git push -u origin $Branch | Out-Host
    } else {
        Write-Host "No origin remote configured. Re-run with -RemoteUrl to enable GitHub sync."
    }
}
finally {
    Pop-Location
}
