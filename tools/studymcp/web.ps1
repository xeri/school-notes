# Serve the study MCP to claude.ai (web + mobile): HTTP server on 127.0.0.1:8765 behind
# the ngrok static domain in local/ngrok-domain. Ctrl+C stops both. Setup: tools/studymcp/README.md.
$ErrorActionPreference = "Stop"
$root = (Resolve-Path "$PSScriptRoot/../..").Path
$domain = (Get-Content "$root/local/ngrok-domain").Trim()
$env:PYTHONUTF8 = "1"
$server = Start-Process uv -ArgumentList "run", "--quiet", "--frozen", "--project", "$root/tools/studymcp", "studymcp", "serve", "--http", "8765" -NoNewWindow -PassThru
try {
    while (-not (Test-Path "$root/local/mcp-token")) { Start-Sleep -Milliseconds 200 }
    $token = (Get-Content "$root/local/mcp-token").Trim()
    Write-Host "`nConnector URL: https://$domain/$token/mcp`n" -ForegroundColor Green
    ngrok http 8765 --url "https://$domain" --log stderr --log-level warn
} finally {
    Stop-Process -Id $server.Id -ErrorAction SilentlyContinue
    Get-CimInstance Win32_Process -Filter "ParentProcessId=$($server.Id)" | ForEach-Object { Stop-Process -Id $_.ProcessId -ErrorAction SilentlyContinue }
}
