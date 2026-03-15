# Oracle Connection Playbook

Objetivo: retomar la conexion a Oracle y APEX sin volver a perder tiempo investigando.

## Estado verificado

Fecha de verificacion: `2026-03-15`

- Repo local: `C:\HT\stp-apex`
- Remoto GitHub: `https://github.com/htroya/stp-apex`
- Rama publicada: `master`
- Conexion visible en VS Code: `hhhhhtroya`
- Usuario de base: `ADMIN`
- Servicio configurado: `HHHHHTROYA_MEDIUM`
- Workspace APEX: `STP`
- `workspace_id`: `9007948669297661`
- Version APEX: `24.2.14`
- Apps de trabajo verificadas: `100` (`test`) y `101` (`test101`)

## Estado funcional actual

- app `100`: base de referencia para export
- app `101`: clon funcional de `100`
- pagina de login de `101`:
  - `https://gc6116f6f9e2d14-hhhhhtroya.adb.us-ashburn-1.oraclecloudapps.com/ords/r/stp/test101/login`
- verificacion HTTP:
  - responde `200`
- verificacion E2E:
  - `tests/playwright/app101-smoke.spec.js` paso correctamente
- paginas actuales de `101`:
  - `0` Global Page
  - `1` Home
  - `9999` Login

## Ruta rapida recomendada

Usar esta prioridad:

1. `ORDS REST Enabled SQL` por HTTPS para automatizacion
2. Conexion Oracle ya abierta en VS Code
3. `SQLcl` manual solo si hace falta una sesion interactiva

Motivo:

- `ORDS` ya quedo probado y responde consultas SQL reales.
- La extension de VS Code puede verse conectada aunque su sesion no siempre sea reutilizable desde automatizacion.
- `SQLcl` desde procesos automatizados puede caer en `ORA-12506`, asi que no conviene arrancar por ahi si `ORDS` esta disponible.

## Opcion 1: ORDS REST Enabled SQL

Esta es la via mas rapida para que Codex ejecute SQL sin pelear con el wallet ni con el listener JDBC.

### Endpoint confirmado

`https://gc6116f6f9e2d14-hhhhhtroya.adb.us-ashburn-1.oraclecloudapps.com/ords/admin/_/sql`

### Prueba minima

```powershell
$user = 'ADMIN'
$pass = Read-Host 'Oracle password' -AsSecureString
$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($pass)
$plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
$pair = "$user`:$plain"
$basic = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($pair))
$headers = @{
  Authorization = "Basic $basic"
  'Content-Type' = 'application/sql'
}

Invoke-RestMethod `
  -Uri 'https://gc6116f6f9e2d14-hhhhhtroya.adb.us-ashburn-1.oraclecloudapps.com/ords/admin/_/sql' `
  -Method Post `
  -Headers $headers `
  -Body "select 'OK' as status from dual"
```

Resultado esperado:

- devuelve una fila con `status = OK`

### Consultas utiles ya verificadas

Version de APEX:

```sql
select version_no
from apex_release;
```

Workspace STP:

```sql
select workspace,
       workspace_id,
       applications,
       allow_app_building_yn,
       allow_sql_workshop_yn
from apex_workspaces
where workspace = 'STP';
```

Sinónimos publicos utiles:

```sql
select owner, synonym_name, table_owner, table_name
from all_synonyms
where synonym_name in (
  'APEX_APPLICATION_INSTALL',
  'APEX_APPLICATION_ADMIN',
  'APEX_EXPORT'
)
order by synonym_name;
```

Paquetes APEX internos ya verificados:

- `APEX_240200.WWV_FLOW_IMP`
- `APEX_240200.WWV_FLOW_IMP_PAGE`
- `APEX_240200.WWV_FLOW_IMP_SHARED`

## Opcion 2: Conexion ya abierta en VS Code

Cuando la extension Oracle aparece conectada, sirve para:

- abrir `SQL Worksheet`
- ejecutar scripts del repo
- navegar objetos
- validar rapido si la base responde

Datos visibles confirmados:

- alias: `hhhhhtroya`
- usuario: `ADMIN`
- tipo: `Cloud Wallet`
- servicio: `HHHHHTROYA_MEDIUM`

Importante:

- la UI puede estar conectada, pero esa autenticacion no siempre se reutiliza desde procesos externos
- no asumir que por estar "connected" ya se puede automatizar por `SQLcl`

## Opcion 3: SQLcl manual

Usarlo solo si hace falta una sesion interactiva real.

### Runtime confirmado

`C:\Users\hernan.troya\AppData\Local\Microsoft\WinGet\Packages\Oracle.SQLcl_Microsoft.Winget.Source_8wekyb3d8bbwe\sqlcl\bin\sql.exe`

### Variables necesarias

```powershell
$env:JAVA_HOME='C:\Users\hernan.troya\.vscode\extensions\oracle.sql-developer-25.4.1-win32-x64\dbtools\jdk'
$env:PATH="$env:JAVA_HOME\bin;$env:PATH"
$env:TNS_ADMIN='C:\Users\hernan.troya\AppData\Roaming\DBTools\connections\nvL1f1LKhg3dUVx2fm3log'
```

### Conexion interactiva

```powershell
sql /nolog
connect ADMIN@hhhhhtroya_medium
```

Notas:

- la clave se ingresa al momento
- no dejarla en scripts versionados
- desde automatizacion se observo `ORA-12506`
- si el objetivo es ejecutar SQL automatizado, volver a `ORDS` antes de gastar tiempo en `SQLcl`

## Wallet y archivos locales

Wallet zip referido por el usuario:

- `C:\Users\hernan.troya\Downloads\Wallet_hhhhhtroya.zip`

Definicion local de la conexion usada por DB Tools:

- `C:\Users\hernan.troya\AppData\Roaming\DBTools\connections\nvL1f1LKhg3dUVx2fm3log`

Archivos relevantes en esa carpeta:

- `dbtools.properties`
- `tnsnames.ora`
- `cwallet.sso`
- `credentials.sso`
- `ojdbc.properties`

Uso practico:

- el wallet sirve para `VS Code` y `SQLcl`
- `ORDS` no necesita wallet

## Lo ya descubierto y no repetir

- `REST Enabled SQL` funciona contra el endpoint `ORDS`
- `select 'OK' from dual` ya fue probado exitosamente por HTTPS
- APEX del entorno es `24.2.14`
- el workspace `STP` existe y tiene `workspace_id = 9007948669297661`
- la extension Oracle guarda la definicion local de conexion, pero no garantiza password reutilizable desde automatizacion
- no vale la pena reinvestigar la URL ORDS ni el workspace ID; ya estan arriba

## Secuencia recomendada para retomar

1. Probar `ORDS` con `select 'OK' from dual`.
2. Confirmar `select version_no from apex_release`.
3. Confirmar `select workspace, workspace_id from apex_workspaces where workspace = 'STP'`.
4. Leer `README.md` y este playbook antes de tocar nada.
5. Ejecutar el SQL de negocio o APEX por `ORDS`.
6. Solo si hace falta UI, abrir VS Code Oracle y usar la conexion `hhhhhtroya`.
7. Solo si hace falta terminal interactiva, usar `SQLcl`.

## Crear una app APEX

### Opcion A: wizard de APEX

Es la forma oficial y mas simple para la primera app:

1. Entrar a `App Builder`.
2. `Create`.
3. `New Application`.
4. Definir nombre, alias y paginas.
5. Ejecutar la app.
6. Exportarla enseguida.

### Opcion B: clonar una app desde un export

Esta es la forma mas util para automatizar nuevas apps a partir de una app base:

1. Tomar un export de una app existente.
2. Importarlo con nuevo `application_id`, `alias` y `name`.
3. Reusar el mismo export como plantilla.

En este repo ya existe un ejemplo real:

- export SQL completo de la app `100`: `C:\HT\stp-apex\apex\exports\f100.sql`
- export split de referencia de la app `100`: `C:\HT\stp-apex\f100.zip`

## Crear una pagina nueva vacia

Si el objetivo es agregar una pagina simple a una app ya existente, no hace falta reinvestigar APIs internas.

Ruta recomendada:

1. Abrir `App Builder`.
2. Entrar a la app, por ejemplo `Application 101`.
3. Click en `Create Page`.
4. Elegir `Blank Page`.
5. Definir numero de pagina, nombre y alias.
6. Crear la pagina.
7. Ejecutar y validar.

Motivo:

- el wizard de APEX es mas rapido para paginas nuevas aisladas
- el repo ya deja automatizado export/import de aplicaciones completas
- no conviene gastar tiempo automatizando creacion de una pagina vacia si el wizard la resuelve en segundos

## Exportar una app

Script:

- `scripts/apex/export-app.ps1`

Ejemplo:

```powershell
.\scripts\apex\export-app.ps1 -ApplicationId 100 -OutputPath .\apex\exports
```

Que hace:

- por defecto usa el endpoint oficial de export de APEX en `ORDS`
- genera un archivo `f<app_id>.sql`
- deja el resultado en la carpeta elegida

Si hace falta export split:

```powershell
.\scripts\apex\export-app.ps1 -ApplicationId 100 -OutputPath .\apex\exports -Split
```

En ese modo:

- prepara `JAVA_HOME`, `PATH` y `TNS_ADMIN`
- conecta con `SQLcl`
- ejecuta `apex export -split`

Notas:

- pide la clave en runtime
- no guarda secretos en el repo
- el flujo recomendado es el export SQL completo
- el export split queda para casos donde realmente se necesita estructura por archivos

## Importar una app

Script:

- `scripts/apex/import-app.ps1`

Ejemplo recomendado con el export SQL completo de la app `100` para crear o reemplazar la app `101`:

```powershell
.\scripts\apex\import-app.ps1 `
  -SourcePath .\apex\exports\f100.sql `
  -TargetApplicationId 101 `
  -TargetApplicationAlias test101 `
  -TargetApplicationName test101 `
  -ReplaceExisting
```

Ejemplo alternativo con el export split:

```powershell
.\scripts\apex\import-app.ps1 `
  -SourcePath .\f100.zip `
  -TargetApplicationId 101 `
  -TargetApplicationAlias test101 `
  -TargetApplicationName test101
```

Que hace:

- usa `ORDS REST Enabled SQL`
- para `.sql`, importa el export completo en una sola ejecucion
- para `.zip`, genera un `offset` una sola vez e importa por lotes
- neutraliza tokens como `&APP_ID.`, `&APP_SESSION.`, `&DEBUG.`, `&APP_USER.` y `&LOGOUT_URL.` para que `ORDS` no cancele la importacion
- valida al final la existencia de la app y el conteo de paginas

Inferencia operativa:

- el flujo principal debe ser `.sql`
- el flujo split sigue siendo util, pero puede requerir validacion funcional adicional
- por eso el script conserva `BatchSize` para `.zip`

## Problema real encontrado y fix

Sintoma observado:

- la app `101` quedaba creada pero vacia o inconsistente
- algunas paginas devolvian `HTTP 400`
- en otros intentos la app quedaba con `page_count = 0`

Causa comprobada:

- `ORDS REST Enabled SQL` intenta resolver tokens SQL*Plus como `&APP_ID.` o `&APP_SESSION.`
- al encontrar esos tokens responde `Substitution cancelled`
- el resto del script deja de ejecutarse aunque la app ya haya sido creada

Prueba minima que reprodujo el problema:

```sql
begin
  dbms_output.put_line('f?p=&APP_ID.:1:&APP_SESSION.::&DEBUG.:::');
end;
/
select 1 as after_statement from dual;
```

Resultado observado:

- solo se ejecuta la primera sentencia
- `ORDS` devuelve `Substitution cancelled`

Nota de diagnostico:

- si en el navegador aparece un error de consola bajo `chrome-extension://` u otra extension, no asumir que es la causa de APEX
- en este caso puntual, ese error era de una extension del navegador; el problema real estaba en la importacion por `ORDS`

Fix aplicado en el repo:

- el importador reemplaza esos tokens por concatenaciones con `chr(38)`
- despues de ese cambio, la app `101` quedo con `3` paginas
- `https://gc6116f6f9e2d14-hhhhhtroya.adb.us-ashburn-1.oraclecloudapps.com/ords/r/stp/test101/login` responde `200`

## Pruebas con Playwright

Archivos:

- `playwright.config.js`
- `tests/playwright/app101-smoke.spec.js`

Prueba minima ya preparada:

- carga la pagina de login de la app `101`
- verifica campos `P9999_USERNAME`, `P9999_PASSWORD` y boton `Sign In`

Ejecucion:

```powershell
npx playwright test tests/playwright/app101-smoke.spec.js
```

Prueba autenticada opcional:

```powershell
$env:APP_URL='https://gc6116f6f9e2d14-hhhhhtroya.adb.us-ashburn-1.oraclecloudapps.com/ords/r/stp/test101'
$env:APP_USERNAME='...'
$env:APP_PASSWORD='...'
npx playwright test tests/playwright/app101-smoke.spec.js
```

Nota:

- si no defines `APP_USERNAME` y `APP_PASSWORD`, solo corre el smoke publico del login
- el smoke publico de la app `101` ya fue ejecutado exitosamente despues del fix del import

## Git y push

Remoto validado:

- `https://github.com/htroya/stp-apex`

Estado actual:

- `origin/master` ya existe
- el push inicial del repo ya se realizo correctamente

Comandos de rutina:

```powershell
git status
git add .
git commit -m "Mensaje claro"
git push
```

Si el push falla con `Repository not found`:

- revisar que el repo exista en GitHub
- revisar la URL de `origin`
- volver a probar con:

```powershell
git remote -v
git remote set-url origin https://github.com/htroya/stp-apex
git push -u origin master
```

## Seguridad

- no guardar passwords en el repo
- no guardar cookies ni URLs con `session=...`
- no commitear el wallet zip ni archivos sensibles
- usar `Read-Host -AsSecureString` o ingreso manual para la clave
