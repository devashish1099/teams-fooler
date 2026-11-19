# keep-active.ps1 - keep Windows / Microsoft Teams from going "Away".
#
# Every 2-4 minutes (random) it sends an F15 keypress. F15 isn't on most
# keyboards and almost no app reacts to it, but Windows counts it as input,
# so the idle timer Teams watches resets. Nothing else is needed.
#
# HOW TO RUN
#   Option A - right-click this file -> "Run with PowerShell".
#
#   Option B - from a terminal (cmd or PowerShell), in this folder:
#       powershell -ExecutionPolicy Bypass -File keep-active.ps1
#
#   Optional: change the interval (seconds):
#       powershell -ExecutionPolicy Bypass -File keep-active.ps1 -MinSeconds 60 -MaxSeconds 180
#
# HOW TO STOP
#   Press Ctrl+C in the window, or just close it.
#
# NOTES
#   -ExecutionPolicy Bypass only applies to this one run; it doesn't change
#   your system settings. Keep MaxSeconds under 300 (Teams' 5-min timeout).

param(
    [int]$MinSeconds = 120,
    [int]$MaxSeconds = 240
)

if ($MinSeconds -gt $MaxSeconds) { $MinSeconds, $MaxSeconds = $MaxSeconds, $MinSeconds }

$shell = New-Object -ComObject WScript.Shell
Write-Host "Keep Active running (F15 every $MinSeconds-$MaxSeconds s). Press Ctrl+C to stop."

while ($true) {
    $shell.SendKeys("{F15}")
    $wait = Get-Random -Minimum $MinSeconds -Maximum ($MaxSeconds + 1)
    Write-Host ("[{0}] ping sent, next in {1}s" -f (Get-Date -Format "HH:mm:ss"), $wait)
    Start-Sleep -Seconds $wait
}
