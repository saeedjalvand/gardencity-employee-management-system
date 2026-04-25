param(
    [string]$OutputPath
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

if (-not $OutputPath) {
    $distDir = Join-Path $projectRoot "dist"
    if (-not (Test-Path -LiteralPath $distDir)) {
        New-Item -ItemType Directory -Path $distDir | Out-Null
    }
    $OutputPath = Join-Path $distDir ("gardencity-deploy-" + $timestamp + ".zip")
}

$excludeDirectoryNames = @(
    ".git",
    "venv",
    ".venv",
    "env",
    "ENV",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "staticfiles",
    "media",
    "dist"
)

$excludeFileNames = @(
    "db.sqlite3",
    "db.sqlite3-journal",
    ".env",
    ".envrc"
)

function Test-IsExcluded {
    param(
        [string]$RelativePath,
        [bool]$IsDirectory
    )

    $parts = $RelativePath -split "[\\/]" | Where-Object { $_ }
    foreach ($part in $parts) {
        if ($excludeDirectoryNames -contains $part) {
            return $true
        }
    }

    if (-not $IsDirectory) {
        $name = [System.IO.Path]::GetFileName($RelativePath)
        if ($excludeFileNames -contains $name) {
            return $true
        }
    }

    return $false
}

function Get-RelativePathSafe {
    param(
        [string]$BasePath,
        [string]$TargetPath
    )

    $normalizedBase = $BasePath.TrimEnd("\", "/")
    if ($TargetPath.Length -le $normalizedBase.Length) {
        return ""
    }

    return $TargetPath.Substring($normalizedBase.Length).TrimStart("\", "/")
}

$stagingRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("gardencity-deploy-" + [guid]::NewGuid().ToString("N"))
$stagingProject = Join-Path $stagingRoot "gardencity-employee-management-system"

try {
    New-Item -ItemType Directory -Path $stagingProject -Force | Out-Null

    $items = Get-ChildItem -LiteralPath $projectRoot -Force -Recurse | Sort-Object FullName
    foreach ($item in $items) {
        $relativePath = Get-RelativePathSafe -BasePath $projectRoot -TargetPath $item.FullName
        if ($relativePath -eq ".") {
            continue
        }

        if (Test-IsExcluded -RelativePath $relativePath -IsDirectory $item.PSIsContainer) {
            continue
        }

        $destinationPath = Join-Path $stagingProject $relativePath
        if ($item.PSIsContainer) {
            New-Item -ItemType Directory -Path $destinationPath -Force | Out-Null
            continue
        }

        $destinationDirectory = Split-Path -Parent $destinationPath
        if (-not (Test-Path -LiteralPath $destinationDirectory)) {
            New-Item -ItemType Directory -Path $destinationDirectory -Force | Out-Null
        }

        Copy-Item -LiteralPath $item.FullName -Destination $destinationPath -Force
    }

    if (Test-Path -LiteralPath $OutputPath) {
        Remove-Item -LiteralPath $OutputPath -Force
    }

    Compress-Archive -Path (Join-Path $stagingProject "*") -DestinationPath $OutputPath -CompressionLevel Optimal
    Write-Host "Deploy package created:"
    Write-Host $OutputPath
}
finally {
    if (Test-Path -LiteralPath $stagingRoot) {
        Remove-Item -LiteralPath $stagingRoot -Recurse -Force
    }
}
