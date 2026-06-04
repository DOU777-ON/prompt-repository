param(
    [string]$RepoRoot
)

$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
    $RepoRoot = Split-Path -Parent $PSScriptRoot
}

$promptsRoot = Join-Path $RepoRoot "Prompts"
$readmePath = Join-Path $promptsRoot "README.md"
$beginMarker = "<!-- BEGIN_AUTO_INDEX -->"
$endMarker = "<!-- END_AUTO_INDEX -->"

function Get-FrontMatter {
    param([string[]]$Lines)

    $meta = [ordered]@{}
    if ($Lines.Count -lt 3 -or $Lines[0].Trim() -ne "---") {
        return $meta
    }

    $end = -1
    for ($i = 1; $i -lt $Lines.Count; $i++) {
        if ($Lines[$i].Trim() -eq "---") {
            $end = $i
            break
        }
    }
    if ($end -lt 0) {
        return $meta
    }

    $currentKey = $null
    for ($i = 1; $i -lt $end; $i++) {
        $line = $Lines[$i]
        if ($line -match "^\s*-\s*(.+?)\s*$" -and $currentKey) {
            if (-not ($meta[$currentKey] -is [System.Collections.IList])) {
                $meta[$currentKey] = New-Object System.Collections.ArrayList
            }
            [void]$meta[$currentKey].Add($Matches[1].Trim(" `"'"))
            continue
        }
        if ($line -match "^\s*([^:#]+):\s*(.*)\s*$") {
            $currentKey = $Matches[1].Trim()
            $value = $Matches[2].Trim()
            if ($value -eq "[]") {
                $meta[$currentKey] = New-Object System.Collections.ArrayList
            } else {
                $meta[$currentKey] = $value.Trim(" `"'")
            }
        }
    }

    return $meta
}

function Get-MetaValue {
    param(
        [hashtable]$Meta,
        [string]$Key,
        [string]$Fallback
    )

    if ($Meta.Contains($Key) -and $Meta[$Key]) {
        if ($Meta[$Key] -is [System.Collections.IList]) {
            return ($Meta[$Key] -join ", ")
        }
        return [string]$Meta[$Key]
    }
    return $Fallback
}

$templateWord = -join ([char]0x6A21, [char]0x677F)
$skipNames = @("README.md", "Prompt_Template.md", "Role_Template.md")
$items = Get-ChildItem -Path $promptsRoot -Recurse -File -Filter "*.md" |
    Where-Object {
        $relative = $_.FullName.Substring($promptsRoot.Length).TrimStart("\", "/")
        ($skipNames -notcontains $_.Name) -and ($relative.IndexOf($templateWord) -lt 0)
    } |
    ForEach-Object {
        $relative = $_.FullName.Substring($promptsRoot.Length).TrimStart("\", "/") -replace "\\", "/"
        $category = Split-Path $relative -Parent
        if (-not $category) { $category = "." }
        $lines = Get-Content -Encoding utf8 -LiteralPath $_.FullName
        $meta = Get-FrontMatter -Lines $lines
        [pscustomobject]@{
            Category = $category
            Title = Get-MetaValue -Meta $meta -Key "title" -Fallback $_.BaseName
            Status = Get-MetaValue -Meta $meta -Key "status" -Fallback ""
            Tags = Get-MetaValue -Meta $meta -Key "tags" -Fallback ""
            Updated = Get-MetaValue -Meta $meta -Key "updated" -Fallback $_.LastWriteTime.ToString("yyyy-MM-dd")
            Path = $relative
        }
    } |
    Sort-Object Category, Title

$indexLines = New-Object System.Collections.Generic.List[string]
if (-not $items -or $items.Count -eq 0) {
    $indexLines.Add("_No prompt entries._")
} else {
    foreach ($group in ($items | Group-Object Category)) {
        $indexLines.Add("### $($group.Name)")
        $indexLines.Add("")
        $indexLines.Add("| Title | Status | Tags | Updated | Path |")
        $indexLines.Add("|---|---|---|---|---|")
        foreach ($item in $group.Group) {
            $path = $item.Path
            $title = $item.Title -replace "\|", "\|"
            $status = $item.Status -replace "\|", "\|"
            $tags = $item.Tags -replace "\|", "\|"
            $updated = $item.Updated -replace "\|", "\|"
            $indexLines.Add("| $title | $status | $tags | $updated | [$path]($path) |")
        }
        $indexLines.Add("")
    }
}

$readme = Get-Content -Encoding utf8 -Raw -LiteralPath $readmePath
$replacement = $beginMarker + "`r`n" + (($indexLines.ToArray()) -join "`r`n").TrimEnd() + "`r`n" + $endMarker

if ($readme -notmatch [regex]::Escape($beginMarker) -or $readme -notmatch [regex]::Escape($endMarker)) {
    $readme = $readme.TrimEnd() + "`r`n`r`n" + $replacement + "`r`n"
} else {
    $pattern = "(?s)" + [regex]::Escape($beginMarker) + ".*?" + [regex]::Escape($endMarker)
    $readme = [regex]::Replace($readme, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $replacement })
}

Set-Content -Encoding utf8 -LiteralPath $readmePath -Value $readme
Write-Host "Updated index: $readmePath"
