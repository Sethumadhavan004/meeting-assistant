# Round 2 batches, thinking off. Run from the repo root, laptop hands-off.
#   .\scripts\run_round2.ps1 -Part ollama   # Granite + Phi (Bonsai server must be STOPPED: one model in RAM)
#   .\scripts\run_round2.ps1 -Part bonsai   # Bonsai (start scripts\start_bonsai.ps1 in its own terminal first)
# Each part: all 10 meetings WITH the system prompt (-> runs-r2.csv), then the held-out m09,m10
# WITHOUT it (-> runs.csv, extending the baseline to 10 meetings).
param([Parameter(Mandatory)][ValidateSet("ollama", "bonsai")][string]$Part)

$py = ".\.venv\Scripts\python.exe"
$sys = "prompts\system\meeting-assistant.md"
$logs = "eval\raw\run-logs"
$models = if ($Part -eq "ollama") { "granite", "phi" } else { "bonsai" }

# Start-Process redirects keep logs in plain text (PowerShell 5.1's *>> would write UTF-16)
function Batch($argList, $name) {
    Start-Process $py -ArgumentList $argList -NoNewWindow -Wait `
        -RedirectStandardOutput "$logs\$name.log" -RedirectStandardError "$logs\$name.err"
}
foreach ($m in $models) {
    Batch "eval_runner.py run --model $m --think off --round r2 --system $sys" "r2_${m}_off"
    Batch "eval_runner.py run --model $m --think off --only m09,m10" "${m}_off_m09-m10"
}
"done $Part $(Get-Date -Format s)" | Out-File -Append -Encoding utf8 "$logs\r2_done.txt"
