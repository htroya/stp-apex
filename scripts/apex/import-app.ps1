param(
    [Parameter(Mandatory = $true)]
    [string]$SourcePath,

    [Parameter(Mandatory = $true)]
    [int]$TargetApplicationId,

    [Parameter(Mandatory = $true)]
    [string]$TargetApplicationAlias,

    [Parameter(Mandatory = $true)]
    [string]$TargetApplicationName,

    [string]$Username = "ADMIN",
    [string]$Workspace = "STP",
    [string]$OrdsSqlUrl = "https://gc6116f6f9e2d14-hhhhhtroya.adb.us-ashburn-1.oraclecloudapps.com/ords/admin/_/sql",
    [int]$BatchSize = 8,
    [switch]$ReplaceExisting
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

function New-BasicHeaders {
    param(
        [string]$User,
        [string]$Password
    )

    $pair = "$User`:$Password"
    $basic = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($pair))
    return @{
        Authorization = "Basic $basic"
        "Content-Type" = "application/sql"
    }
}

function Invoke-OrdsSql {
    param(
        [string]$Sql,
        [hashtable]$Headers,
        [string]$Url
    )

    return Invoke-RestMethod -Uri $Url -Method Post -Headers $Headers -Body $Sql -TimeoutSec 240
}

function Get-CleanSql {
    param(
        [string]$Content,
        [string]$Path,
        [string]$TargetName
    )

    $cleaned = ($Content -split "`r?`n" | Where-Object {
        $_ -notmatch '^\s*(prompt|set\s|whenever\s+sqlerror|@@|--|$)'
    }) -join "`n"

    switch ($Path) {
        "application/create_application.sql" {
            $cleaned = $cleaned.Replace("p_logo_text=>'test'", "p_logo_text=>'$TargetName'")
            $cleaned = $cleaned.Replace("p_substitution_value_01=>'test'", "p_substitution_value_01=>'$TargetName'")
        }
        "application/pages/page_00001.sql" {
            $cleaned = $cleaned.Replace("p_step_title=>'test'", "p_step_title=>'$TargetName'")
            $cleaned = $cleaned.Replace("p_plug_name=>'test'", "p_plug_name=>'$TargetName'")
        }
        "application/pages/page_09999.sql" {
            $cleaned = $cleaned.Replace("p_step_title=>'test - Log In'", "p_step_title=>'$TargetName - Log In'")
            $cleaned = $cleaned.Replace("p_plug_name=>'test'", "p_plug_name=>'$TargetName'")
        }
        "application/user_interfaces.sql" {
            $cleaned = $cleaned.Replace(
                "p_home_url=>'f?p=&APP_ID.:1:&APP_SESSION.::&DEBUG.:::'",
                "p_home_url=>'f?p='||chr(38)||'APP_ID.:1:'||chr(38)||'APP_SESSION.::'||chr(38)||'DEBUG.:::'"
            )
            $cleaned = $cleaned.Replace(
                "p_login_url=>'f?p=&APP_ID.:LOGIN:&APP_SESSION.::&DEBUG.:::'",
                "p_login_url=>'f?p='||chr(38)||'APP_ID.:LOGIN:'||chr(38)||'APP_SESSION.::'||chr(38)||'DEBUG.:::'"
            )
        }
    }

    foreach ($token in @("APP_ID", "APP_SESSION", "APP_USER", "DEBUG", "LOGOUT_URL")) {
        $cleaned = $cleaned.Replace("&$token.", "'||chr(38)||'$token.")
    }

    return $cleaned
}

function Get-Offset {
    param(
        [hashtable]$Headers,
        [string]$Url
    )

    $sql = @'
begin
  apex_application_install.generate_offset;
end;
/
select apex_application_install.get_offset as generated_offset
from dual;
'@

    $result = Invoke-OrdsSql -Sql $sql -Headers $Headers -Url $Url
    return [int64]$result.items[1].resultSet.items[0].generated_offset
}

function Get-ZipEntriesInInstallOrder {
    param([string]$ZipPath)

    Add-Type -AssemblyName System.IO.Compression.FileSystem

    $zip = [IO.Compression.ZipFile]::OpenRead($ZipPath)
    try {
        $installEntry = $zip.Entries |
            Where-Object { $_.FullName -match '^[^/]+/install\.sql$' } |
            Select-Object -First 1
        if (-not $installEntry) {
            throw "No se encontro un install.sql en la raiz del export dentro del zip."
        }

        $rootFolder = [IO.Path]::GetDirectoryName($installEntry.FullName).Replace('\', '/')

        $reader = New-Object IO.StreamReader($installEntry.Open())
        try {
            $installSql = $reader.ReadToEnd()
        }
        finally {
            $reader.Dispose()
        }

        $entries = @()
        foreach ($line in ($installSql -split "`r?`n")) {
            if ($line -match '^@@application/(.+)$') {
                $entries += "application/" + $Matches[1].Trim()
            }
        }

        $contentMap = @{}
        foreach ($entryPath in $entries) {
            $entry = $zip.GetEntry("$rootFolder/$entryPath")
            if (-not $entry) {
                throw "No se encontro la entrada $rootFolder/$entryPath en el zip."
            }

            $r = New-Object IO.StreamReader($entry.Open())
            try {
                $contentMap[$entryPath] = $r.ReadToEnd()
            }
            finally {
                $r.Dispose()
            }
        }

        return @{
            Root = $rootFolder
            Order = $entries
            Content = $contentMap
        }
    }
    finally {
        $zip.Dispose()
    }
}

function Get-Batches {
    param(
        [string[]]$Items,
        [int]$Size
    )

    $batches = @()
    for ($i = 0; $i -lt $Items.Count; $i += $Size) {
        $take = [Math]::Min($Size, $Items.Count - $i)
        $batches += ,($Items[$i..($i + $take - 1)])
    }
    return $batches
}

function Assert-NoStatementErrors {
    param(
        [object]$Result,
        [string]$Context
    )

    $errors = @(
        $Result.items | Where-Object {
            $_.PSObject.Properties.Name -contains "errorCode" -and $null -ne $_.errorCode
        }
    )

    if ($errors.Count -gt 0) {
        $errors | ConvertTo-Json -Depth 8
        throw "Fallo durante $Context."
    }
}

$securePassword = Read-Host "Oracle password" -AsSecureString
$plainPassword = Get-PlainTextPassword -SecurePassword $securePassword
$headers = New-BasicHeaders -User $Username -Password $plainPassword

if ($ReplaceExisting) {
    $existsSql = @"
select count(*) as app_count
from apex_applications
where application_id = $TargetApplicationId
"@

    $exists = Invoke-OrdsSql -Sql $existsSql -Headers $headers -Url $OrdsSqlUrl
    if ([int]$exists.items[0].resultSet.items[0].app_count -gt 0) {
        $removeSql = @"
begin
  apex_application_install.set_workspace('$Workspace');
  apex_application_install.remove_application($TargetApplicationId);
end;
/
"@

        Invoke-OrdsSql -Sql $removeSql -Headers $headers -Url $OrdsSqlUrl | Out-Null
    }
}

$extension = [IO.Path]::GetExtension($SourcePath).ToLowerInvariant()

if ($extension -eq ".sql") {
    $scriptContent = Get-Content -Raw -LiteralPath $SourcePath
    $scriptContent = Get-CleanSql -Content $scriptContent -Path "" -TargetName $TargetApplicationName

    $override = @"
begin
  apex_application_install.set_application_id($TargetApplicationId);
  apex_application_install.set_application_alias('$TargetApplicationAlias');
  apex_application_install.set_application_name('$TargetApplicationName');
  apex_application_install.generate_offset;
end;
/
"@

    $importResult = Invoke-OrdsSql -Sql ($override + "`n" + $scriptContent) -Headers $headers -Url $OrdsSqlUrl
    Assert-NoStatementErrors -Result $importResult -Context "la importacion SQL"
}
elseif ($extension -eq ".zip") {
    $zipInfo = Get-ZipEntriesInInstallOrder -ZipPath $SourcePath
    $offset = Get-Offset -Headers $headers -Url $OrdsSqlUrl

    $setEnvironment = Get-CleanSql -Content $zipInfo.Content["application/set_environment.sql"] -Path "application/set_environment.sql" -TargetName $TargetApplicationName
    $endEnvironment = Get-CleanSql -Content $zipInfo.Content["application/end_environment.sql"] -Path "application/end_environment.sql" -TargetName $TargetApplicationName

    $allFiles = $zipInfo.Order | Where-Object { $_ -notin @("application/set_environment.sql", "application/end_environment.sql") }
    $batches = Get-Batches -Items $allFiles -Size $BatchSize

    $batchNumber = 0
    foreach ($batch in $batches) {
        $batchNumber++

        $override = @"
begin
  apex_application_install.clear_all;
  apex_application_install.set_application_id($TargetApplicationId);
  apex_application_install.set_application_alias('$TargetApplicationAlias');
  apex_application_install.set_application_name('$TargetApplicationName');
  apex_application_install.set_offset($offset);
end;
/
"@

        $parts = New-Object System.Collections.Generic.List[string]
        $parts.Add($override)
        $parts.Add($setEnvironment)

        foreach ($entryPath in $batch) {
            $parts.Add((Get-CleanSql -Content $zipInfo.Content[$entryPath] -Path $entryPath -TargetName $TargetApplicationName))
        }

        $parts.Add($endEnvironment)
        $sql = [string]::Join("`n", $parts)

        Write-Host "Importando lote $batchNumber/$($batches.Count): $($batch -join ', ')"
        $result = Invoke-OrdsSql -Sql $sql -Headers $headers -Url $OrdsSqlUrl
        Assert-NoStatementErrors -Result $result -Context "el lote $batchNumber"
    }
}
else {
    throw "Formato no soportado: $SourcePath. Use .zip o .sql"
}

$checkSql = @"
select application_id, application_name, alias
from apex_applications
where application_id = $TargetApplicationId
"@

$pageSql = @"
select count(*) as page_count
from apex_application_pages
where application_id = $TargetApplicationId
"@

$check = Invoke-OrdsSql -Sql $checkSql -Headers $headers -Url $OrdsSqlUrl
$pages = Invoke-OrdsSql -Sql $pageSql -Headers $headers -Url $OrdsSqlUrl

[pscustomobject]@{
    application = $check.items[0].resultSet.items
    page_count  = $pages.items[0].resultSet.items[0].page_count
} | ConvertTo-Json -Depth 8
