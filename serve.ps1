# Запуск сервера с лимитами загрузки и локальным временным каталогом (Windows).
Set-Location $PSScriptRoot

$uploadTmp = Join-Path $PSScriptRoot 'storage\framework\uploads'
$publicTickets = Join-Path $PSScriptRoot 'public\uploads\tickets'
$storageTickets = Join-Path $PSScriptRoot 'storage\app\public\tickets'

foreach ($dir in @($uploadTmp, $publicTickets, $storageTickets)) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# php -S must receive -d upload_tmp_dir (see scripts/run-dev-server.php); parent artisan -d is not enough.
php scripts/run-dev-server.php @args
