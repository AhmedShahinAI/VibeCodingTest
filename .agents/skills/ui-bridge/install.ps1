# install.ps1 - Install ui-generate-from-plan skill on Windows PowerShell

$ErrorActionPreference = "Stop"

$SkillDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillName = "ui-gernreate-from-plan"
$ClaudeGlobal = Join-Path $env:USERPROFILE ".claude"
$CodexGlobal = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
$ClaudeLocal = ".claude"
$CodexLocal = ".codex"

Write-Host "Installing $SkillName skill..."

function Copy-SkillFiles($Destination) {
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null

    foreach ($item in @("SKILL.md","README.md","requirements.txt","package.json")) {
        $source = Join-Path $SkillDir $item
        if (Test-Path $source) {
            Copy-Item -Force $source $Destination
        }
    }

    foreach ($dir in @("scripts","subskills","references","templates","agents",".claude",".codex")) {
        $source = Join-Path $SkillDir $dir
        if (Test-Path $source) {
            Copy-Item -Recurse -Force $source $Destination
        }
    }
}

$ClaudeSkill = Join-Path $ClaudeGlobal "skills\$SkillName"
Copy-SkillFiles $ClaudeSkill
Write-Host "  OK Claude skill files copied to $ClaudeSkill"

$CodexSkill = Join-Path $CodexGlobal "skills\$SkillName"
Copy-SkillFiles $CodexSkill
Write-Host "  OK Codex skill files copied to $CodexSkill"

New-Item -ItemType Directory -Force -Path (Join-Path $ClaudeGlobal "commands") | Out-Null
Copy-Item -Force (Join-Path $SkillDir ".claude\commands\*.md") (Join-Path $ClaudeGlobal "commands")
Write-Host "  OK Claude commands installed to $(Join-Path $ClaudeGlobal "commands")"

New-Item -ItemType Directory -Force -Path (Join-Path $ClaudeLocal "commands") | Out-Null
Copy-Item -Force (Join-Path $SkillDir ".claude\commands\*.md") (Join-Path $ClaudeLocal "commands")
Write-Host "  OK Project Claude commands installed to $(Join-Path $ClaudeLocal "commands")"

$CodexAliasSource = Join-Path $SkillDir ".codex\skills"
$CodexAliasTarget = Join-Path $CodexGlobal "skills"
New-Item -ItemType Directory -Force -Path $CodexAliasTarget | Out-Null
Copy-Item -Recurse -Force (Join-Path $CodexAliasSource "*") $CodexAliasTarget
Write-Host "  OK Codex alias skills installed to $CodexAliasTarget"

$CodexLocalAliasTarget = Join-Path $CodexLocal "skills"
New-Item -ItemType Directory -Force -Path $CodexLocalAliasTarget | Out-Null
Copy-Item -Recurse -Force (Join-Path $CodexAliasSource "*") $CodexLocalAliasTarget
Write-Host "  OK Project Codex alias skills installed to $CodexLocalAliasTarget"

$pythonOk = $false
try {
    $pyVer = (python --version 2>&1).ToString().Trim()
    Write-Host "  OK Python found: $pyVer"
    $pythonOk = $true
} catch {}
if (-not $pythonOk) {
    try {
        $pyVer = (python3 --version 2>&1).ToString().Trim()
        Write-Host "  OK Python found: $pyVer"
        $pythonOk = $true
    } catch {}
}
if (-not $pythonOk) {
    Write-Host "  WARN python3 not found -- install Python 3.8+ from https://python.org"
}

try {
    npx.cmd --version 2>$null | Out-Null
    Write-Host "Installing Impeccable (optional validation layer)..."
    try {
        npx.cmd impeccable install --providers=claude 2>$null
        Write-Host "  OK Impeccable installed"
    } catch {
        Write-Host "  WARN Impeccable install failed -- internal rules still apply"
    }
} catch {
    Write-Host "  WARN npx.cmd not found -- Impeccable CLI validation disabled"
}

Write-Host ""
Write-Host "OK $SkillName installed successfully"
Write-Host ""
Write-Host "Restart your agent, then use:"
Write-Host "  /ui-plan or `$ui-plan"
Write-Host "  /ui-implement or `$ui-implement"
Write-Host "  /ui-link-html-to-plan or `$ui-link-html-to-plan"
Write-Host "  /ui-into-preview or `$ui-into-preview"
Write-Host ""
Write-Host "Docs: https://github.com/rakymat-plugins/ui-gernreate-from-plan"
