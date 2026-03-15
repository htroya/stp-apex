param(
    [Parameter(Mandatory = $true)]
    [int]$ApplicationId,

    [string]$OutputPath = ".\apex\exports",
    [switch]$Split,
    [string]$Username = "ADMIN",
    [string]$OrdsSqlUrl = "https://gc6116f6f9e2d14-hhhhhtroya.adb.us-ashburn-1.oraclecloudapps.com/ords/admin/_/sql",
    [string]$ServiceAlias = "hhhhhtroya_medium",
    [string]$SqlExe = "C:\Users\hernan.troya\AppData\Local\Microsoft\WinGet\Packages\Oracle.SQLcl_Microsoft.Winget.Source_8wekyb3d8bbwe\sqlcl\bin\sql.exe",
    [string]$JavaHome = "C:\Users\hernan.troya\.vscode\extensions\oracle.sql-developer-25.4.1-win32-x64\dbtools\jdk",
    [string]$TnsAdmin = "C:\Users\hernan.troya\AppData\Roaming\DBTools\connections\nvL1f1LKhg3dUVx2fm3log"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-PlainTextPassword {
    param([Security.SecureString]$SecurePassword)

    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecurePassword)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
}

$securePassword = Read-Host "Oracle password" -AsSecureString
$plainPassword = Get-PlainTextPassword -SecurePassword $securePassword

New-Item -ItemType Directory -Force -Path $OutputPath | Out-Null

if ($Split) {
    if (-not (Test-Path -LiteralPath $SqlExe)) {
        throw "No se encontro SQLcl en: $SqlExe"
    }

    $env:JAVA_HOME = $JavaHome
    $env:PATH = "$JavaHome\bin;$env:PATH"
    $env:TNS_ADMIN = $TnsAdmin

    $sqlScript = @"
connect $Username/"$plainPassword"@$ServiceAlias
apex export -applicationid $ApplicationId -split
exit
"@

    Push-Location $OutputPath
    try {
        $sqlScript | & $SqlExe /nolog
    }
    finally {
        Pop-Location
    }
}
else {
    $pair = "$Username`:$plainPassword"
    $basic = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($pair))
    $headers = @{
        Authorization = "Basic $basic"
    }
    $targetFile = Join-Path $OutputPath ("f{0}.sql" -f $ApplicationId)
    $ordsBaseUrl = $OrdsSqlUrl -replace '/sql$',''
    $exportUrl = "$ordsBaseUrl/db-api/stable/apex/applications/${ApplicationId}?export_format=SQL_SCRIPT&export_type=APPLICATION_SOURCE&p_with_original_ids=true"

    Invoke-WebRequest -Uri $exportUrl -Headers $headers -Method Get -OutFile $targetFile -TimeoutSec 240 | Out-Null

    Write-Host "Export creado en $targetFile"
}
