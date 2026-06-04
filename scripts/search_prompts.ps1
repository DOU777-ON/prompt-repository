param(
    [string]$Query,
    [string]$Tag,
    [string]$Status,
    [string]$Category,
    [string]$RepoRoot
)

$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
    $RepoRoot = Split-Path -Parent $PSScriptRoot
}

$promptsRoot = Join-Path $RepoRoot "Prompts"

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
$results = Get-ChildItem -Path $promptsRoot -Recurse -File -Filter "*.md" |
    Where-Object {
        $relative = $_.FullName.Substring($promptsRoot.Length).TrimStart("\", "/")
        ($skipNames -notcontains $_.Name) -and ($relative.IndexOf($templateWord) -lt 0)
    } |
    ForEach-Object {
        $relative = $_.FullName.Substring($promptsRoot.Length).TrimStart("\", "/") -replace "\\", "/"
        $lines = Get-Content -Encoding utf8 -LiteralPath $_.FullName
        $content = $lines -join "`n"
        $meta = Get-FrontMatter -Lines $lines
        $record = [pscustomobject]@{
            Title = Get-MetaValue -Meta $meta -Key "title" -Fallback $_.BaseName
            Category = Get-MetaValue -Meta $meta -Key "category" -Fallback (Split-Path $relative -Parent)
            Status = Get-MetaValue -Meta $meta -Key "status" -Fallback ""
            Tags = Get-MetaValue -Meta $meta -Key "tags" -Fallback ""
            Updated = Get-MetaValue -Meta $meta -Key "updated" -Fallback $_.LastWriteTime.ToString("yyyy-MM-dd")
            Path = $relative
            Content = $content
        }

        $match = $true
        if ($Query) {
            $needle = [regex]::Escape($Query)
            $match = $match -and (($record.Title -match $needle) -or ($record.Tags -match $needle) -or ($record.Content -match $needle))
        }
        if ($Tag) {
            $match = $match -and ($record.Tags -match [regex]::Escape($Tag))
        }
        if ($Status) {
            $match = $match -and ($record.Status -eq $Status)
        }
        if ($Category) {
            $match = $match -and (($record.Category -match [regex]::Escape($Category)) -or ($record.Path -match [regex]::Escape($Category)))
        }

        if ($match) {
            $record | Select-Object Title, Category, Status, Tags, Updated, Path
        }
    } |
    Sort-Object Category, Title

if ($results) {
    $results | Format-Table -AutoSize
} else {
    Write-Host "No prompts found."
}
