# start_bonsai.ps1 - start the Bonsai 4B llama-server with every eval setting written out.
#
# Why not the demo's start_llama_server.ps1: for the 4B model it silently adds a vision
# projector (+0.37 GB RAM), a presence penalty of 1.0, and auto server slots, and the only
# installed binary is the Vulkan build, which can offload prompt work to the iGPU.
# Every flag here is explicit so the run is CPU-only and matches the Ollama runs.
#
# Run in its OWN PowerShell window and leave it open (the server dies with the window):
#   cd D:\projects\meeting-assistant
#   .\scripts\start_bonsai.ps1
# Stop with Ctrl+C. The startup + request log is saved to eval\raw\server-logs\.

$Root  = Split-Path $PSScriptRoot -Parent
$Demo  = Join-Path $Root "models\Bonsai-demo"
$Bin   = Join-Path $Demo "bin\vulkan\llama-server.exe"
$Model = Join-Path $Demo "models\bonsai2-gguf\4B\Ternary-Bonsai-2-4B-PQ2_0.gguf"

$ServerArgs = @(
    "-m", $Model,
    "--host", "127.0.0.1", "--port", "8080",
    "--device", "none",          # no GPU device at all: weights AND prompt ops stay on CPU
    "-ngl", "0",                 # zero layers on GPU (belt and braces with --device none)
    "-c", "4096",                # same context as Ollama (num_ctx 4096 in eval_runner.py)
    "-np", "1",                  # one slot, so the full 4096 context is available to one request
    "-fa", "on",                 # flash attention, same as the demo script
    "--jinja",                   # use the model's chat template; needed for enable_thinking per request
    "--presence-penalty", "0",   # Ollama default; a penalty changes greedy picks even at temperature 0
    "--no-mmproj"                # text-only eval: don't load the vision projector
)

$LogDir = Join-Path $Root "eval\raw\server-logs"
New-Item -ItemType Directory -Force $LogDir | Out-Null
$Stamp = "{0:yyyyMMdd-HHmmss}" -f (Get-Date)
$Log = Join-Path $LogDir "bonsai-$Stamp.log"

# Save the exact command next to the log, so every log says which settings produced it.
"$Bin $($ServerArgs -join ' ')" | Set-Content -Encoding utf8 (Join-Path $LogDir "bonsai-$Stamp.cmd.txt")

Write-Host "Starting: $Bin"
Write-Host "Args:     $($ServerArgs -join ' ')"
Write-Host "Log:      $Log"

# --log-file: the server writes its own plain-text log and still prints to this window.
# (Piping through Tee-Object instead writes UTF-16 in Windows PowerShell and locks the file.)
& $Bin @ServerArgs --log-file $Log
