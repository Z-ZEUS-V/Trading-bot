$ErrorActionPreference = "Stop"

$python = "C:\Python312\python.exe"
$checker = Join-Path $PSScriptRoot "check_kraken_futures_key.py"
$keyPlain = $null
$secretSecure = $null
$secretPtr = [IntPtr]::Zero
$exitCode = 1

try {
    $keyPlain = Read-Host "API key pública de Derivatives (se mostrará en pantalla)"
    $secretSecure = Read-Host "API secret privada de Derivatives (entrada oculta)" -AsSecureString

    if ([string]::IsNullOrWhiteSpace($keyPlain) -or $secretSecure.Length -eq 0) {
        Write-Host "Resultado: falta una credencial; no se envió ninguna petición a Kraken."
        exit 2
    }

    $secretPtr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secretSecure)
    $env:KRAKEN_FUTURES_API_KEY = $keyPlain.Trim()
    $env:KRAKEN_FUTURES_API_SECRET = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($secretPtr)

    & $python $checker
    $exitCode = $LASTEXITCODE
}
finally {
    Remove-Item Env:KRAKEN_FUTURES_API_KEY -ErrorAction SilentlyContinue
    Remove-Item Env:KRAKEN_FUTURES_API_SECRET -ErrorAction SilentlyContinue
    if ($secretPtr -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($secretPtr)
    }
    $keyPlain = $null
    $secretSecure = $null
}

exit $exitCode
