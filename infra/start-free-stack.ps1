$ErrorActionPreference = "Stop"

docker info *> $null
if ($LASTEXITCODE -ne 0) {
    throw "No container daemon is running. Start Docker Desktop or Podman, then run this script again."
}

function Ensure-Container {
    param([string]$Name, [scriptblock]$Create)
    $existing = docker ps -a --filter "name=^/$Name$" --format "{{.Names}}"
    if ($existing -eq $Name) { docker start $Name | Out-Null } else { & $Create }
    if ($LASTEXITCODE -ne 0) { throw "Failed to start container $Name" }
}

if (-not (docker network ls --filter "name=^cct-platform$" --format "{{.Name}}")) {
    docker network create cct-platform | Out-Null
}
Ensure-Container "cct-mongo" {
    docker run -d --name cct-mongo --network cct-platform --restart unless-stopped -v cct-orion-mongo:/data/db mongo:4.4 --wiredTigerCacheSizeGB 0.5 | Out-Null
}
Ensure-Container "cct-orion" {
    docker run -d --name cct-orion --network cct-platform --restart unless-stopped -p 1026:1026 quay.io/fiware/orion-ld:1.12.0 -dbhost cct-mongo | Out-Null
}
Ensure-Container "cct-minio" {
    docker run -d --name cct-minio --network cct-platform --restart unless-stopped -p 9000:9000 -p 9001:9001 -e MINIO_ROOT_USER=criticalcare -e MINIO_ROOT_PASSWORD=criticalcare-local -v cct-minio-data:/data quay.io/minio/minio:latest server /data --console-address :9001 | Out-Null
}
Write-Host "Free digital-twin stack started."
Write-Host "Orion-LD: http://127.0.0.1:1026/version"
Write-Host "MinIO console: http://127.0.0.1:9001"
