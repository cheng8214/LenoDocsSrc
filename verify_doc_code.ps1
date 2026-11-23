# verify_doc_code.ps1 -- run every ```leno block in the given docs and fail on any non-zero exit
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File verify_doc_code.ps1 [-Exe <leno.exe>] <md> [md...]
#   默认（不给参数）= 新手三篇：
#       Leno零基础入门.md / 安装与第一个项目.md / 常见任务cookbook.md
#
# 为什么需要它：文档里的代码是**会被照抄**的，写错一个 `:` 或者拿 `=` 当初值，
#   代价比代码里写错高得多（读者会以为语言就是这样）。本脚本把每个含 `main(` 的
#   ```leno 块写成临时文件、用真编译器跑一遍 —— 只有跑通才算文档过关。
#
# 口径：
#   · 只跑**看起来完整**的块（含 `main(`）；片段（表达式演示）跳过 —— 它们没法单独运行
#   · 块里 `import "x.leno"` 的跳过（需要同目录的兄弟文件，属"多文件示例"，单独验）
#   · 只看**退出码**：编译错误 / 运行期错误 / 崩溃都会非零，一律算失败
#   · 本文件必须保持 **ASCII-only**（Windows PowerShell 5.1 按 ANSI 解析 .ps1，
#     中文会被拆成命令）——中文说明一律写进 docs，不写进脚本
param(
    [string]$Exe = "",
    [string[]]$Md = @()
)

$ErrorActionPreference = "Stop"

if (-not $Exe) {
    # 默认找兄弟仓 Leno/build/leno.exe（本仓与 Leno 仓平级）
    $cand = Join-Path (Split-Path $PSScriptRoot -Parent) "Leno\build\leno.exe"
    if (Test-Path $cand) { $Exe = $cand }
}
if (-not $Exe -or -not (Test-Path $Exe)) {
    Write-Host "leno.exe not found. Pass it explicitly: -Exe D:\path\to\leno.exe" -ForegroundColor Red
    exit 2
}

if ($Md.Count -eq 0) {
    $Md = @(
        (Join-Path $PSScriptRoot ("Leno" + [char]0x96F6 + [char]0x57FA + [char]0x7840 + [char]0x5165 + [char]0x95E8 + ".md")),
        (Join-Path $PSScriptRoot ([char]0x5B89 + [char]0x88C5 + [char]0x4E0E + [char]0x7B2C + [char]0x4E00 + [char]0x4E2A + [char]0x9879 + [char]0x76EE + ".md")),
        (Join-Path $PSScriptRoot ([char]0x5E38 + [char]0x89C1 + [char]0x4EFB + [char]0x52A1 + "cookbook" + ".md"))
    )
}

$work = Join-Path $env:TEMP ("verify_doc_" + [guid]::NewGuid().ToString("N").Substring(0, 8))
New-Item -ItemType Directory -Path $work | Out-Null

$totalRan = 0
$totalFail = 0

foreach ($file in $Md) {
    if (-not (Test-Path $file)) { Write-Host ("missing md: " + $file) -ForegroundColor Red; $totalFail++; continue }
    $text = [System.IO.File]::ReadAllText($file, [System.Text.Encoding]::UTF8)
    $blocks = ([regex]'(?s)```leno\r?\n(.*?)```').Matches($text)
    $ran = 0; $fail = 0; $skip = 0; $i = 0
    foreach ($b in $blocks) {
        $i++
        $code = $b.Groups[1].Value
        if ($code -notmatch 'main\s*\(') { $skip++; continue }
        if ($code -match 'import\s+"[^"]+\.leno"') { $skip++; continue }
        $f = Join-Path $work ((Split-Path $file -Leaf) + "." + $i + ".leno")
        [System.IO.File]::WriteAllText($f, $code, (New-Object System.Text.UTF8Encoding($false)))
        $out = & $Exe $f 2>&1 | Out-String
        $rc = $LASTEXITCODE
        $ran++
        if ($rc -ne 0) {
            $fail++
            Write-Host ("[FAIL] " + (Split-Path $file -Leaf) + " block#" + $i) -ForegroundColor Red
            ($out -split "`r?`n" | Where-Object { $_ -match 'error|warning|崩溃' } | Select-Object -First 4) |
                ForEach-Object { Write-Host ("       " + $_) }
        }
    }
    $color = "Green"; if ($fail -gt 0) { $color = "Red" }
    Write-Host ("{0}: ran={1} fail={2} skipped(fragment/multi-file)={3}" -f (Split-Path $file -Leaf), $ran, $fail, $skip) -ForegroundColor $color
    $totalRan += $ran
    $totalFail += $fail
}

Write-Host ("TOTAL ran={0} fail={1}" -f $totalRan, $totalFail)
if ($totalFail -gt 0) { exit 1 }
Write-Host "ALL DOC CODE BLOCKS OK" -ForegroundColor Green
