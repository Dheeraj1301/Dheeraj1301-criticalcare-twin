$ErrorActionPreference = "Stop"
foreach ($name in @("cct-orion", "cct-mongo", "cct-minio")) {
    if (docker ps --filter "name=^/$name$" --format "{{.Names}}") { docker stop $name | Out-Null }
}
Write-Host "Free digital-twin stack stopped. Persistent volumes were retained."
